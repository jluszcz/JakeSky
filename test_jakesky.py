#!/usr/bin/env python

import jakesky
import unittest

from datetime import date
from datetime import datetime

class TestJakeSky(unittest.TestCase):

    def setUp(self):
        self.hours = [8, 12, 18]

        today = date.today()
        self.y = today.year
        self.m = today.month
        self.d = today.day

        self.weekday_days = [date(2017, 12, d) for d in range(3, 8)]
        self.weekend_days = [date(2017, 12, d) for d in range(8, 10)]

    def test_get_hours_of_interest_current_after_hours(self):
        current_time = datetime(self.y, self.m, self.d, hour=23)
        self.assertEquals([], jakesky.get_hours_of_interest(current_time, hours=self.hours, add_weekend_hour=False))

    def test_get_hours_of_interest_current_before_hours(self):
        current_time = datetime(self.y, self.m, self.d, hour=6)
        self.assertEquals([8, 12, 18], jakesky.get_hours_of_interest(current_time, hours=self.hours, add_weekend_hour=False))

    def test_get_hours_of_interest_current_almost_next_hours(self):
        current_time = datetime(self.y, self.m, self.d, hour=7)
        self.assertEquals([12, 18], jakesky.get_hours_of_interest(current_time, hours=self.hours, add_weekend_hour=False))

    def test_get_hours_of_interest_current_between_hours(self):
        current_time = datetime(self.y, self.m, self.d, hour=9)
        self.assertEquals([12, 18], jakesky.get_hours_of_interest(current_time, hours=self.hours, add_weekend_hour=False))

    def test_get_hours_of_interest_weekend(self):
        for d in self.weekday_days:
            self.assertEquals([8, 12, 18], jakesky.get_hours_of_interest(datetime(d.year, d.month, d.day), hours=self.hours, add_weekend_hour=True))

        for d in self.weekend_days:
            self.assertEquals([8, 12, 18, 22], jakesky.get_hours_of_interest(datetime(d.year, d.month, d.day), hours=self.hours, add_weekend_hour=True))

    def test_get_speakable_weather_summary(self):
        self.assertEquals('Drizzling', jakesky.get_speakable_weather_summary('Drizzle'))

if __name__ == '__main__':
    unittest.main()
