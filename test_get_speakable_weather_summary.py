import jakesky

def test_get_speakable_weather_summary():
    assert 'Drizzling' == jakesky.get_speakable_weather_summary('Drizzle')
    assert 'Raining' == jakesky.get_speakable_weather_summary('Raining')
