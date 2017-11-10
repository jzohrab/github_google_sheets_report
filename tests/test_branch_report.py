# -*- coding: utf-8 -*-

# import context
from .context import GitHubRepoAnalyzer
from GitHubRepoAnalyzer import branch_report

from .fakes import FakeGitRepo

import unittest
import os
import json
import yaml
import datetime
import pytz

class GitBranchesTestSuite(unittest.TestCase):
    """Basic test cases."""

    def setUp(self):
        fake_repo = FakeGitRepo()
        config = None
        currdir = os.path.dirname(os.path.abspath(__file__))
        config_file = os.path.join(currdir, 'fake_config.yml')
        with open(config_file, 'r') as f:
            config = yaml.load(f)
        reference_date = datetime.datetime.strptime('2017-10-29', "%Y-%m-%d")
        toronto = pytz.timezone('America/Toronto')
        reference_date = pytz.utc.localize(reference_date)

        self.branch_report = branch_report.GitBranches(config, fake_repo, reference_date)
        self.maxDiff = None

    def test_data_matches_expected(self):
        currdir = os.path.dirname(os.path.abspath(__file__))
        expected_file = os.path.join(currdir, 'data', 'expected_results', 'test_branch_report.json')
        expected_data = None
        with open(expected_file, 'r') as f:
            expected_data = json.load(f)

        actual = json.dumps(self.branch_report.load_data(), indent=2, sort_keys=True)
        expected = json.dumps(expected_data, indent=2, sort_keys=True)
        self.assertEqual(actual, expected)

    def test_git_days_ago(self):
        self.assertEqual(self.branch_report.git_days_elapsed('2017-10-27'), 2)

    def test_dataframe_works(self):
        df = self.branch_report.load_dataframe()
        # If we reach here, we're ok.
        # Higher-level integration tests will cover the accuracy ...
        # should move those tests down here.

if __name__ == '__main__':
    unittest.main()
