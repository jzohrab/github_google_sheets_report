# -*- coding: utf-8 -*-

from .context import GitHubRepoAnalyzer
from GitHubRepoAnalyzer import pull_reqs

from .fakes import FakeGitHubApi

import unittest
import os
import json
import yaml


class PullRequestsTestSuite(unittest.TestCase):
    """Basic test cases."""

    def setUp(self):
        fake_api = FakeGitHubApi()
        config = None
        currdir = os.path.dirname(os.path.abspath(__file__))
        config_file = os.path.join(currdir, 'fake_config.yml')
        with open(config_file, 'r') as f:
            config = yaml.load(f)
        self.prs = pull_reqs.GitHubPullRequests(config, fake_api)
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


if __name__ == '__main__':
    unittest.main()
