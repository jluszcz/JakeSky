#!/usr/bin/env python

import argparse
import gzip
import json
import logging
import os
import pytz
import requests
import sys

from collections import namedtuple
from datetime import datetime

CACHE_FILE = '/tmp/darksky.json.gz'

Weather = namedtuple('Weather', ['timestamp', 'summary', 'temperature'])


def setup_logging(verbose=False):
    """Sets up logging using the default python logger, at INFO or DEBUG, depending on the value of verbose"""

    logger = logging.getLogger()
    logger.setLevel(logging.INFO if not verbose else logging.DEBUG)


def parse_args(raw_args=None):
    if raw_args is None:
        raw_args = sys.argv[1:]

    parser = argparse.ArgumentParser(description='Retrieve Jake-specific weather')
    parser.add_argument('--verbose', '-v', dest='verbose', action='store_true', help='If provided, log at DEBUG instead of INFO.')
    parser.add_argument('--use-cache', action='store_true',
                        help='If provided, use a cached response from the last time DarkSky was queried.')
    parser.add_argument('--latitude', type=float, default=os.environ.get('JAKESKY_LATITUDE'),
                        help='North is positive, South is negative.')
    parser.add_argument('--longitude', type=float, default=os.environ.get('JAKESKY_LONGITUDE'),
                        help='East is positive, West is negative.')

    args = parser.parse_args(args=raw_args)

    if not args.latitude:
        raise ValueError('--latitude or a default JAKESKY_LATITUDE is required')
    if not args.longitude:
        raise ValueError('--longitude or a default JAKESKY_LONGITUDE is required')

    return args


def query_dark_sky(latitude, longitude, use_cache=False):
    """
    Queries DarkSky using the key from JAKESKY_KEY and returns the current and hourly forecast as a dict.
    See https://darksky.net/dev/docs/response for a description of the response format.
    """

    if use_cache and os.path.isfile(CACHE_FILE):
        logging.debug('Using cached result from %s', CACHE_FILE)
        with gzip.open(CACHE_FILE, 'rb') as f:
            return json.loads(f.read())

    key = os.environ['JAKESKY_KEY']

    # Since we only care about the current and hourly forecast for specific times, exclude some of the data in the response.
    url = 'https://api.darksky.net/forecast/%s/%f,%f?exclude=minutely,daily,flags' % (key, latitude, longitude)
    headers = {'Accept-Encoding': 'gzip'}

    logging.debug('Querying %s', url)
    response = requests.get(url, headers=headers)
    response.raise_for_status()

    logging.debug('%s', response.text)

    logging.debug('Writing result to %s', CACHE_FILE)
    with gzip.open(CACHE_FILE, 'wb') as f:
        f.write(response.text)

    return json.loads(response.text)


def parse_weather(dark_sky_response):
    """Retrieves relevant weather information from a DarkSky API response, returning a list of Weathers."""

    timezone = pytz.timezone(dark_sky_response['timezone'])
    now = datetime.fromtimestamp(dark_sky_response['currently']['time'], timezone)

    hours_of_interest = get_hours_of_interest(now)

    weather = [Weather(now, dark_sky_response['currently']['summary'], dark_sky_response['currently']['temperature'])]

    for hourly_weather in dark_sky_response['hourly']['data']:
        hourly_weather_time = datetime.fromtimestamp(hourly_weather['time'], timezone)

        if hourly_weather_time.date() > now.date():
            logging.debug('%s is no longer relevant', hourly_weather_time)
            break

        if hourly_weather_time.hour == now.hour:
            logging.debug('Skipping current hour: %d', now.hour)
            continue

        if hourly_weather_time.hour in hours_of_interest:
            weather.append(Weather(hourly_weather_time, hourly_weather['summary'], hourly_weather['temperature']))

    for w in weather:
        logging.info('%s: %s (%f)', w.timestamp, w.summary, w.temperature)

    return weather


def get_hours_of_interest(current_time, hours=None, add_weekend_hour=True):
    """Return the hours of interest for today's forecast"""

    if not hours:
        hours = [8, 12, 18]
    else:
        hours = list(hours)

    current_hour = current_time.hour

    if add_weekend_hour and current_time.weekday() in [4, 5]:
        hours.append(22)

    hours_of_interest = []

    hours = sorted(hours)
    for n in range(len(hours)):
        if current_hour + 1 < hours[n]:
            hours_of_interest = hours[n:]
            break

    logging.debug('Hours of interest: %s', hours_of_interest)
    return hours_of_interest


def get_speakable_timestamp(timestamp):
    """Return a 'speakable' timestamp, e.g. 8am, noon, 9pm, etc."""

    speakable = '%s %s' % (timestamp.strftime('%I').lstrip('0'), timestamp.strftime('%p'))
    if speakable == '12 PM':
        return 'noon'
    elif speakable == '12 AM':
        return 'midnight'
    return speakable


def build_text_to_speak(weather):
    to_speak = []

    # The first entry is assumed to be the current time, and there should always be at least one entry
    current = weather[0]

    to_speak.append('It\'s currently %s.' % get_speakable_weather(current))

    # Remaining entries are in the future
    for w in weather[1:]:
        to_speak.append('At %s, it will be %s.' % (get_speakable_timestamp(w.timestamp), get_speakable_weather(w)))

    # Stick an 'And' on the final entry if there is more than one
    if len(to_speak) > 1:
        to_speak[-1] = 'And ' + to_speak[-1][0].lower() + to_speak[-1][1:]

    text_to_speak = ' '.join(to_speak)

    logging.info('Will Speak: %s', text_to_speak)

    return text_to_speak


def get_speakable_weather(weather):
    return '%d and %s' % (weather.temperature, get_speakable_weather_summary(weather.summary))


def get_speakable_weather_summary(summary):
    if summary.lower() == 'drizzle':
        return 'Drizzling'
    return summary


def main():
    """Entry point for running as a CLI"""

    args = parse_args()
    setup_logging(args.verbose)

    response = query_dark_sky(args.latitude, args.longitude, use_cache=args.use_cache)
    weather = parse_weather(response)
    build_text_to_speak(weather)


def alexa_handler(event, context):
    """Entry point for Lambda"""

    setup_logging()

    # If calling from a scheduled event, this is only a 'warmup' call
    if event.get('detail-type') == 'Scheduled Event':
        logging.info('Not executing jakesky during warmup call')
        return

    # The only other caller of this lambda should be the JakeSky Alexa skill
    if event['session']['application']['applicationId'] != os.environ['JAKESKY_SKILL_ID']:
        logging.error('Invalid application ID: %s, expected: %s',
                      event['session']['application']['applicationId'], os.environ['JAKESKY_SKILL_ID'])
        raise ValueError('Invalid application ID')

    logging.debug('Event:\n%s', json.dumps(event))

    response = query_dark_sky(float(os.environ['JAKESKY_LATITUDE']), float(os.environ['JAKESKY_LONGITUDE']))
    weather = parse_weather(response)
    to_speak = build_text_to_speak(weather)

    return {
        'version': '1.0',
        'response': {
            'outputSpeech': {
                'type': 'PlainText',
                'text': to_speak
            }
        }
    }


if __name__ == '__main__':
    main()
