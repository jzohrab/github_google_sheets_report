# -*- coding: utf-8 -*-

# import context
from .context import GitHubRepoAnalyzer
from GitHubRepoAnalyzer import github_report

from .fakes import FakeGitRepo
from .fakes import FakeGitHubApi

import unittest
import os
import json
import yaml


class GitHubReportTestSuite(unittest.TestCase):

    def setUp(self):
        fake_repo = FakeGitRepo()
        fake_api = FakeGitHubApi()

        config = None
        currdir = os.path.dirname(os.path.abspath(__file__))
        config_file = os.path.join(currdir, 'fake_config.yml')
        with open(config_file, 'r') as f:
            config = yaml.load(f)
        
        self.ghr = github_report.GitHubReport(config, fake_repo, fake_api)
        self.maxDiff = None

    def test_data_is_processed(self):
        data = self.ghr.build_report()
        data.sort(key = lambda d: d['branch_name'])
        actual = json.dumps(data, indent=2, sort_keys=True)

        currdir = os.path.dirname(os.path.abspath(__file__))
        expected_file = os.path.join(currdir, 'data', 'expected_results', 'test_github_report.json')
        expected = None
        with open(expected_file, 'r') as f:
            expected = json.load(f)
        expected.sort(key = lambda d: d['branch_name'])
        expected = json.dumps(expected, indent=2, sort_keys=True)
        self.assertEqual(actual, expected)

    def test_pandas(self):
        df = self.ghr.build_dataframe()
        print(df)

if __name__ == '__main__':
    unittest.main()
