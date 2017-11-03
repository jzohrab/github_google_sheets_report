# -*- coding: utf-8 -*-

# import context
from .context import GitHubRepoAnalyzer as ghr
from GitHubRepoAnalyzer import github_report as gr

from .fakes import FakeGitRepo
from .fakes import FakeGitHubApi

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
        self.assertEqual(gr.TimeUtils.human_elapsed_time(self.now, d), "Some time in the future (?)")

    def assert_desc_equals(self, expected_msg, s = 0, m = 0, h = 0, d = 0):
        other_date = self.now - datetime.timedelta(seconds = s, minutes = m, hours = h, days = d)
        self.assertEqual(gr.TimeUtils.human_elapsed_time(self.now, other_date), expected_msg)
        
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

class GitHubReportTestSuite(unittest.TestCase):

    def setUp(self):
        fake_repo = FakeGitRepo()
        fake_api = FakeGitHubApi()

        config = None
        currdir = os.path.dirname(os.path.abspath(__file__))
        config_file = os.path.join(currdir, 'fake_config.yml')
        with open(config_file, 'r') as f:
            config = yaml.load(f)

        reference_date = datetime.datetime.strptime('2017-10-29', "%Y-%m-%d")
        toronto = pytz.timezone('America/Toronto')
        reference_date = pytz.utc.localize(reference_date)

        self.ghr = gr.GitHubReport(config, fake_repo, fake_api, reference_date)
        self.maxDiff = None

    def test_build_report(self):
        df = self.ghr.build_dataframe()
        actual = df.to_csv()
        currdir = os.path.dirname(os.path.abspath(__file__))
        expected_file = os.path.join(currdir, 'data', 'expected_results', 'test_github_report.csv')
        expected = ''
        with open(expected_file, 'r') as f:
            expected = f.read()
        self.assertEqual(actual.strip(), expected.strip())

if __name__ == '__main__':
    unittest.main()
