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
        # with open(expected_file, 'w') as f:
        #     f.write(actual)
        with open(expected_file, 'r') as f:
            expected = f.read()
        self.assertEqual(actual.strip(), expected.strip())

    def test_git_days_ago(self):
        self.assertEqual(self.ghr.git_days_elapsed('2017-10-27'), 2)

if __name__ == '__main__':
    unittest.main()
