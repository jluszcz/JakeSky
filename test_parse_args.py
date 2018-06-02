import jakesky

import mock
import pytest

LATITUDE = 30.0
LONGITUDE = 45.0


def test_parse_args_provided():
    raw_args = ['--latitude', str(LATITUDE), '--longitude', str(LONGITUDE)]

    args = jakesky.parse_args(raw_args)

    assert LATITUDE == args.latitude
    assert LONGITUDE == args.longitude


def test_parse_args_longitude_missing(mocker):
    raw_args = ['--latitude', str(LATITUDE)]

    mocker.patch('os.environ.get', return_value=None)

    with pytest.raises(ValueError):
        jakesky.parse_args(raw_args)


def test_parse_args_latitude_missing(mocker):
    raw_args = ['--longitude', str(LONGITUDE)]

    mocker.patch('os.environ.get', return_value=None)

    with pytest.raises(ValueError):
        jakesky.parse_args(raw_args)


def test_parse_args_default_env_vars(mocker):
    raw_args = []

    mocker.patch('os.environ.get', return_value=str(LATITUDE))

    args = jakesky.parse_args(raw_args)

    assert LATITUDE == args.latitude
    assert LATITUDE == args.longitude
