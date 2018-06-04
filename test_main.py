import jakesky

import mock


# This test is trivial, but the expectation is that main() is going to get more complicated in future commits
def test_main(mocker):
    args_mock = mock.MagicMock()
    args_mock.verbose = False

    parse_args_mock = mocker.patch('jakesky.parse_args', return_value=args_mock)
    get_geo_mock = mocker.patch('jakesky.get_geo_coordinates', return_value=(0.0, 0.0, ))
    query_dark_sky_mock = mocker.patch('jakesky.query_dark_sky')
    parse_weather_mock = mocker.patch('jakesky.parse_weather')
    build_text_mock = mocker.patch('jakesky.build_text_to_speak')

    jakesky.main()

    parse_args_mock.assert_called_once()
    get_geo_mock.assert_called_once()
    query_dark_sky_mock.assert_called_once()
    parse_weather_mock.assert_called_once()
    build_text_mock.assert_called_once()
