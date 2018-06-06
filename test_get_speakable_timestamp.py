import jakesky

from datetime import datetime

def _get_timestamp(hour):
    return datetime(2018, 6, 3, hour)


def test_noon():
    ts = _get_timestamp(12)
    assert 'noon' == jakesky.get_speakable_timestamp(ts)


def test_midnight():
    ts = _get_timestamp(0)
    assert 'midnight' == jakesky.get_speakable_timestamp(ts)


def test_morning():
    ts = _get_timestamp(9)
    assert '9 AM' == jakesky.get_speakable_timestamp(ts)


def test_evening():
    ts = _get_timestamp(21)
    assert '9 PM' == jakesky.get_speakable_timestamp(ts)
