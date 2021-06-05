import jakesky

def test_get_speakable_weather_summary():
    assert 'Drizzling' == jakesky.get_speakable_weather_summary('Drizzle')
    assert 'Raining' == jakesky.get_speakable_weather_summary('Raining')


def test_get_speakable_weather():
    assert '65 and Sunny' == jakesky.get_speakable_weather(jakesky.Weather('2021-06-05T00:00:00Z', 'Sunny', 65.45))
