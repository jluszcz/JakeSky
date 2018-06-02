import jakesky

import pytest

from datetime import date, datetime


HOURS = [8, 12, 18]


@pytest.fixture
def current_date():
    return date.today()


def _get_time(date, hour):
    return datetime(date.year, date.month, date.day, hour=hour)


def test_get_hours_of_interest_current_after_hours(current_date):
    assert [] == jakesky.get_hours_of_interest(_get_time(current_date, 23), hours=HOURS, add_weekend_hour=False)


def test_get_hours_of_interest_current_before_hours(current_date):
    assert [8, 12, 18] == jakesky.get_hours_of_interest(_get_time(current_date, 6), hours=HOURS, add_weekend_hour=False)


def test_get_hours_of_interest_current_almost_next_hours(current_date):
    assert [12, 18] == jakesky.get_hours_of_interest(_get_time(current_date, 7), hours=HOURS, add_weekend_hour=False)


def test_get_hours_of_interest_current_between_hours(current_date):
    assert [12, 18] == jakesky.get_hours_of_interest(_get_time(current_date, 9), hours=HOURS, add_weekend_hour=False)


def test_get_hours_of_interest_weekday():
    weekdays = [date(2017, 12, d) for d in range(3, 8)]

    for d in weekdays:
        assert [8, 12, 18] == jakesky.get_hours_of_interest(datetime(d.year, d.month, d.day), hours=HOURS, add_weekend_hour=True)


def test_get_hours_of_interest_weekend():
    weekends = [date(2017, 12, d) for d in range(8, 10)]

    for d in weekends:
        assert [8, 12, 18, 22] == jakesky.get_hours_of_interest(datetime(d.year, d.month, d.day), hours=HOURS, add_weekend_hour=True)
