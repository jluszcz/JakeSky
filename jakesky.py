#!/usr/bin/env python

import argparse
import gzip
import json
import logging
import os
import pytz
import requests
import sys
import time

from collections import namedtuple
from datetime import datetime

CACHE_FILE = '/tmp/darksky.json.gz'

Weather = namedtuple('Weather', ['timestamp', 'summary', 'temperature'])


def setup_logging(verbose=False):
    """Sets up logging using the default python logger, at INFO or DEBUG, depending on the value of verbose"""

    logger = logging.getLogger()
    logger.setLevel(logging.INFO if not verbose else logging.DEBUG)


def parse_args(raw_args=None):
    if raw_args is None: # pragma: no cover
        raw_args = sys.argv[1:]

    parser = argparse.ArgumentParser(description='Retrieve Jake-specific weather')
    parser.add_argument('--verbose', '-v', dest='verbose', action='store_true', help='If provided, log at DEBUG instead of INFO.')
    parser.add_argument('--use-cache', action='store_true',
                        help='If provided, use a cached response from the last time DarkSky was queried.')
    parser.add_argument('--address', default=os.environ.get('JAKESKY_ADDRESS'),
                        help='Address in "street city state zipcode" format.')

    args = parser.parse_args(args=raw_args)

    if not args.address:
        raise ValueError('--address or a default JAKESKY_ADDRESS is required')

    return args


def _query_url(description, url, headers=None, params=None, timeout=0.5):
    def _log_optional(optional):
        return json.dumps(optional) if optional else None

    logging.debug('Querying %s url=%s, headers=%s, params=%s', description, url, _log_optional(headers), _log_optional(params))
    start_time = time.time()
    response = requests.get(url, headers=headers, params=params, timeout=timeout)
    response.raise_for_status()
    logging.info('Query to %s returned in %0.2f sec', description, time.time() - start_time)

    response = response.json()

    logging.debug('Query to %s returned: %s', description, json.dumps(response))

    return response


def query_dark_sky(latitude, longitude, use_cache=False):
    """
    Queries DarkSky using the key from JAKESKY_DARKSKY_KEY and returns the current and hourly forecast as a dict.
    See https://darksky.net/dev/docs/response for a description of the response format.
    """

    if use_cache and os.path.isfile(CACHE_FILE):
        logging.debug('Using cached result from %s', CACHE_FILE)
        with gzip.open(CACHE_FILE, 'rb') as f:
            return json.loads(f.read())

    key = os.environ['JAKESKY_DARKSKY_KEY']

    # Since we only care about the current and hourly forecast for specific times, exclude some of the data in the response.
    url = 'https://api.darksky.net/forecast/%s/%f,%f?exclude=minutely,daily,flags' % (key, latitude, longitude)
    headers = {
        'Accept': 'application/json',
        'Accept-Encoding': 'gzip',
    }

    response = _query_url('DarkSky', url, headers=headers)

    if use_cache:
        logging.debug('Writing result to %s', CACHE_FILE)
        with gzip.open(CACHE_FILE, 'wb') as f:
            json.dump(response, f)

    return response


def parse_weather(dark_sky_response):
    """Retrieves relevant weather information from a DarkSky API response, returning a list of Weathers."""

    timezone = pytz.timezone(dark_sky_response['timezone'])
    now = datetime.fromtimestamp(dark_sky_response['currently']['time'], timezone)

    hours_of_interest = get_hours_of_interest(now, add_weekend_hour=False)

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
        logging.info('%s: %s (%0.2f)', w.timestamp, w.summary, w.temperature)

    return weather


def get_hours_of_interest(current_time, hours=None, add_weekend_hour=True):
    """Return the hours of interest for today's forecast"""

    if hours is None: # pragma: no cover
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


def split_address_string(address_string):
    parts = address_string.split()
    if len(parts) < 4:
        raise ValueError('address_string "%s" does not appear to be an address' % address_string)

    return ' '.join(parts[:-3]), parts[-3], parts[-2], parts[-1]


def get_geo_coordinates(address_string=None, event=None):
    latitude = os.environ.get('JAKESKY_LATITUDE')
    longitude = os.environ.get('JAKESKY_LONGITUDE')
    if latitude is not None and longitude is not None:
        logging.debug('Using specified latitude/longitude: %s, %s', latitude, longitude)
        return float(latitude), float(longitude)
    elif address_string:
        logging.debug('Using specified address: %s', address_string)
        address, city, state, postal_code = split_address_string(address_string)
    elif event:
        logging.debug('Looking up address via Alexa device location')
        address, city, state, postal_code = get_alexa_device_location(event)
    else:
        raise ValueError('latitude/longitude, address_string, or event must be provided')

    return query_geocodio(address, city, state, postal_code)


def get_alexa_device_location(event):
    base_url = event['context']['System']['apiEndpoint']
    device_id = event['context']['System']['device']['deviceId']
    api_token = event['context']['System']['apiAccessToken']

    headers = {
        'Accept': 'application/json',
        'Authorization': 'Bearer %s' % api_token
    }

    url = '%s/v1/devices/%s/settings/address' % (base_url, device_id)

    response = _query_url('Alexa Device Location', url, headers=headers)

    assert 'US' == response['countryCode']
    return response['addressLine1'], response['city'], response['stateOrRegion'], response['postalCode']


def query_geocodio(street, city, state, postal_code):
    url = 'https://api.geocod.io/v1.3/geocode'
    params = {
        'street': street,
        'city': city,
        'state': state,
        'postal_code': postal_code,
        'api_key': os.environ['JAKESKY_GEOCODIO_KEY'],
    }

    headers = {
        'Accept': 'application/json'
    }

    response = _query_url('Geocodio', url, headers=headers, params=params)

    assert 1 == len(response['results'])
    result = response['results'][0]

    return result['location']['lat'], result['location']['lng']


def alexa_handler(event, context, env_vars=None):
    """Entry point for Lambda"""

    if env_vars is None: # pragma: no cover
        env_vars = os.environ

    setup_logging()

    # If calling from a scheduled event, this is only a 'warmup' call
    if event.get('detail-type') == 'Scheduled Event':
        logging.info('Warmup only, returning early')
        return

    logging.debug('Event:\n%s', json.dumps(event))

    latitude, longitude = get_geo_coordinates(event=event)
    response = query_dark_sky(latitude, longitude)
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


def main():
    """Entry point for running as a CLI"""

    args = parse_args()
    setup_logging(args.verbose)

    logging.debug('Args: %s', args)

    latitude, longitude = get_geo_coordinates(address_string=args.address)
    response = query_dark_sky(latitude, longitude, use_cache=args.use_cache)
    weather = parse_weather(response)
    build_text_to_speak(weather)


if __name__ == '__main__': # pragma: no cover
    main()
