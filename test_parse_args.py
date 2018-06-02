import jakesky

import mock
import pytest

ADDRESS = '200 Clarendon Ave Boston MA 02116'

def test_parse_args_provided():
    raw_args = ['--address', ADDRESS]

    args = jakesky.parse_args(raw_args)

    assert ADDRESS == args.address


def test_parse_args_address_missing(mocker):
    raw_args = []

    mocker.patch('os.environ.get', return_value=None)

    with pytest.raises(ValueError):
        jakesky.parse_args(raw_args)


def test_parse_args_default_env_vars(mocker):
    raw_args = []

    mocker.patch('os.environ.get', return_value=ADDRESS)

    args = jakesky.parse_args(raw_args)

    assert ADDRESS == args.address
