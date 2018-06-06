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

ENV = {
    'JAKESKY_SKILL_ID': SKILL_ID
}

def _test_alexa_handler(mocker, event=dict(EVENT), env_vars=dict(ENV), expect_calls=True):
    context = MagicMock()

    get_geo_mock = mocker.patch('jakesky.get_geo_coordinates', return_value=(0, 0, ))
    query_dark_sky_mock = mocker.patch('jakesky.query_dark_sky')
    parse_weather_mock = mocker.patch('jakesky.parse_weather')
    build_text_mock = mocker.patch('jakesky.build_text_to_speak')

    mocks = [get_geo_mock, query_dark_sky_mock, parse_weather_mock, build_text_mock]

    jakesky.alexa_handler(event, context, env_vars)

    for m in mocks:
        if expect_calls:
            m.assert_called_once()
        else:
            m.assert_not_called()


def test_alexa_handler_scheduled_event(mocker):
    _test_alexa_handler(mocker, event={'detail-type': 'Scheduled Event'}, expect_calls=False)


def test_alexa_handler_wrong_skill_id(mocker):
    with pytest.raises(ValueError):
        _test_alexa_handler(mocker, env_vars={'JAKESKY_SKILL_ID': 'wrong-skill-id'}, expect_calls=False)


def test_alexa_handler(mocker):
    _test_alexa_handler(mocker, expect_calls=True)
