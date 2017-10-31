# -*- coding: utf-8 -*-

# import context
from .context import GitHubRepoAnalyzer
from GitHubRepoAnalyzer import branch_report

import unittest
import os
import json
import yaml

class FakeGitRepo:
    """Fake class implementing the GitHubApi API"""
    def get_git_cmd_response(self, cmd):
        currdir = os.path.dirname(os.path.abspath(__file__))
        cachedir = os.path.join(currdir, 'data', 'fake_git_responses')
        filename = cmd.translate({ord(c):'_' for c in "/:. \"%=-"})
        data = os.path.join(cachedir, filename)
        with open(data, 'r') as f:
            rawdata = f.read()
        return [line for line in rawdata.split("\n") if line.strip() != '']

class FakeGitRepo_SanityChecks(unittest.TestCase):

    def setUp(self):
        self.fake_repo = FakeGitRepo()

    def test_fake(self):
        """Testing the fake class!"""
        cmd = "git log --date=short --format=\"%cd %an\" origin/develop..origin/feature_1_success_only"
        data = self.fake_repo.get_git_cmd_response(cmd)
        self.assertTrue(True)  # Sanity check only.
        

class GitBranchesTestSuite(unittest.TestCase):
    """Basic test cases."""

    def setUp(self):
        fake_repo = FakeGitRepo()
        config = None
        currdir = os.path.dirname(os.path.abspath(__file__))
        config_file = os.path.join(currdir, 'fake_config.yml')
        with open(config_file, 'r') as f:
            config = yaml.load(f)
        self.branch_report = branch_report.GitBranches(config, fake_repo)
        self.maxDiff = None

    def test_data_is_processed(self):
        currdir = os.path.dirname(os.path.abspath(__file__))
        expected_file = os.path.join(currdir, 'data', 'expected_results', 'test_branch_report.json')
        expected_data = None
        with open(expected_file, 'r') as f:
            expected_data = json.load(f)

        actual = json.dumps(self.branch_report.load_data(), indent=2, sort_keys=True)
        expected = json.dumps(expected_data, indent=2, sort_keys=True)
        self.assertEqual(actual, expected)


if __name__ == '__main__':
    unittest.main()
