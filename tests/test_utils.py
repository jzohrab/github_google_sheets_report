# -*- coding: utf-8 -*-

# import context
from .context import GitHubRepoAnalyzer as ghr
from GitHubRepoAnalyzer.utils import TimeUtils

import unittest
import os
import json
import yaml
import datetime
import pytz

class TimeUtilsTestSuite(unittest.TestCase):
    def setUp(self):
        self.now = datetime.datetime.now()

    def test_future(self):
        d = self.now + datetime.timedelta(seconds = 1)
        self.assertEqual(TimeUtils.human_elapsed_time(self.now, d), "Some time in the future (?)")

    def assert_desc_equals(self, expected_msg, s = 0, m = 0, h = 0, d = 0):
        other_date = self.now - datetime.timedelta(seconds = s, minutes = m, hours = h, days = d)
        self.assertEqual(TimeUtils.human_elapsed_time(self.now, other_date), expected_msg)
        
    def test_mins(self):
        self.assert_desc_equals("Just now")
        self.assert_desc_equals("< 1 minute ago", s = 10)
        self.assert_desc_equals("< 1 minute ago", s = 59)
        self.assert_desc_equals("1 minute ago", s = 60)
        self.assert_desc_equals("1 minute ago", s = 60 + 30)
        self.assert_desc_equals("1 minute ago", s = 2 * 60 - 1)
        self.assert_desc_equals("2 minutes ago", s = 2 * 60)
        self.assert_desc_equals("5 minutes ago", s = 5 * 60)
        self.assert_desc_equals("5 minutes ago", s = 5 * 60 + 30)
        self.assert_desc_equals("59 minutes ago", s = 59 * 60 + 30)
        self.assert_desc_equals("1 hour ago", s = 60 * 60)
        self.assert_desc_equals("1 hour ago", s = 60 * 60 + 5 * 60)
        self.assert_desc_equals("1 hour ago", s = 60 * 60 + 59 * 60 + 59)
        self.assert_desc_equals("2 hours ago", s = 2 * 60 * 60)
        self.assert_desc_equals("23 hours ago", s = 24 * 60 * 60 - 1)
        self.assert_desc_equals("1 day ago", s = 24 * 60 * 60)
        self.assert_desc_equals("1 day ago", s = 2 * 24 * 60 * 60 - 1)
        self.assert_desc_equals("2 days ago", s = 3 * 24 * 60 * 60 - 1)
        self.assert_desc_equals("29 days ago", s = 30 * 24 * 60 * 60 - 1)
        self.assert_desc_equals("1 month ago", s = 30 * 24 * 60 * 60)
        self.assert_desc_equals("2 months ago", s = 2 * 30 * 24 * 60 * 60)
        self.assert_desc_equals("2 months ago", s = 3 * 30 * 24 * 60 * 60 - 1)
        self.assert_desc_equals("3 months ago", s = 3 * 30 * 24 * 60 * 60)
        self.assert_desc_equals("6 months ago", s = 6 * 30 * 24 * 60 * 60)
        self.assert_desc_equals("6 months ago", s = 6 * 30 * 24 * 60 * 60 + 1)
        self.assert_desc_equals("6 months ago", s = 7 * 30 * 24 * 60 * 60 - 1)
        self.assert_desc_equals("> 6 months ago", s = 7 * 30 * 24 * 60 * 60)


if __name__ == '__main__':
    unittest.main()
