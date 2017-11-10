# -*- coding: utf-8 -*-

from .context import GitHubRepoAnalyzer
from GitHubRepoAnalyzer import pull_reqs

from .fakes import FakeGitHubApi

import unittest
import os
import json
import yaml
import datetime
import pytz


class PullRequestsTestSuite(unittest.TestCase):
    """Basic test cases."""

    def setUp(self):
        fake_api = FakeGitHubApi()
        config = None
        currdir = os.path.dirname(os.path.abspath(__file__))
        config_file = os.path.join(currdir, 'fake_config.yml')
        with open(config_file, 'r') as f:
            config = yaml.load(f)
        reference_date = datetime.datetime.strptime('2017-10-29', "%Y-%m-%d")
        toronto = pytz.timezone('America/Toronto')
        reference_date = pytz.utc.localize(reference_date)
        self.prs = pull_reqs.GitHubPullRequests(config, fake_api, reference_date)
        self.maxDiff = None

    def test_data_is_processed(self):
        currdir = os.path.dirname(os.path.abspath(__file__))
        expected_file = os.path.join(currdir, 'data', 'expected_results', 'test_pull_requests.json')
        expected_data = None
        with open(expected_file, 'r') as f:
            expected_data = json.load(f)

        actual = json.dumps(self.prs.load_data(), indent=2, sort_keys=True)
        expected = json.dumps(expected_data, indent=2, sort_keys=True)
        self.assertEqual(actual, expected)

    def test_dataframe_works(self):
        df = self.prs.load_dataframe()
        # If we reach here, we're ok.
        # Higher-level integration tests will cover the accuracy ...
        # should move those tests down here.

if __name__ == '__main__':
    unittest.main()
