import jakesky

import pytest
from mock import MagicMock

SKILL_ID = '1234'

EVENT = {
    'session': {
        'application': {
            'applicationId': SKILL_ID
        }
    }
}


def _test_alexa_handler(mocker, event=dict(EVENT), expect_calls=True):
    context = MagicMock()

    get_geo_mock = mocker.patch('jakesky.get_geo_coordinates', return_value=(0, 0, ))
    query_dark_sky_mock = mocker.patch('jakesky.query_dark_sky')
    parse_weather_mock = mocker.patch('jakesky.parse_weather')
    build_text_mock = mocker.patch('jakesky.build_text_to_speak')

    mocks = [get_geo_mock, query_dark_sky_mock, parse_weather_mock, build_text_mock]

    jakesky.alexa_handler(event, context)

    for m in mocks:
        if expect_calls:
            m.assert_called_once()
        else:
            m.assert_not_called()


def test_alexa_handler_scheduled_event(mocker):
    _test_alexa_handler(mocker, event={'detail-type': 'Scheduled Event'}, expect_calls=False)


def test_alexa_handler(mocker):
    _test_alexa_handler(mocker, expect_calls=True)
