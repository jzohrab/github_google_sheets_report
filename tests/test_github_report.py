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
        self.ghr.build_report()


if __name__ == '__main__':
    unittest.main()
