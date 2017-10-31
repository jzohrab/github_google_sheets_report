# -*- coding: utf-8 -*-

# import context
from .context import GitHubRepoAnalyzer
from GitHubRepoAnalyzer import pull_reqs

import unittest
import os
import json
import yaml

class FakeGitHubApi:
    """Fake class implementing the GitHubApi API"""
    def get_json(self, url, params=None):
        """Gets data from file."""
        currdir = os.path.dirname(os.path.abspath(__file__))
        cachedir = os.path.join(currdir, 'data', 'fake_github_api_json')
        filename = url.translate({ord(c):'_' for c in "/:."})
        cachefile = os.path.join(cachedir, filename)
    
        with open(cachefile, 'r') as f:
            ret = json.load(f)
        return ret

class FakeGitHubApi_SanityChecks(unittest.TestCase):

    def setUp(self):
        fake_api = FakeGitHubApi()

    def test_fake_api(self):
        """Testing the fake class!"""
        fake_api = FakeGitHubApi()
        data = fake_api.get_json("https://api.github.com/repos/jeff-zohrab/demo_gitflow_pulls")
        self.assertTrue(True)  # Sanity check only.
        

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
