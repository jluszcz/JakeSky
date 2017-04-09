#!/usr/bin/env python

import jakesky
import unittest

class TestJakeSky(unittest.TestCase):

    def test_get_hours_of_interest_current_after_hours(self):
        self.assertEquals([], jakesky.get_hours_of_interest(current_hour=23, hours=[8, 12, 18]))

    def test_get_hours_of_interest_current_before_hours(self):
        self.assertEquals([8, 12, 18], jakesky.get_hours_of_interest(current_hour=6, hours=[8, 12, 18]))

    def test_get_hours_of_interest_current_between_hours(self):
        self.assertEquals([12, 18], jakesky.get_hours_of_interest(current_hour=9, hours=[8, 12, 18]))

if __name__ == '__main__':
    unittest.main()
