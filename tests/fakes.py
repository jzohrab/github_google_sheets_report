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
        # print(data)
        self.assertTrue(True)  # Sanity check only.
        

class FakeGitHubApi:
    """Fake class implementing the GitHubApi API"""
    def get_json(self, url):
        """Gets data from file."""
        currdir = os.path.dirname(os.path.abspath(__file__))
        cachedir = os.path.join(currdir, 'data', 'fake_github_api_json')
        filename = url.translate({ord(c):'_' for c in "/:.?&="})
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
        data = fake_api.get_json("https://api.github.com/repos/jeff-zohrab/demo_gitflow_pulls?state=open&base=develop")
        # print(data)
        self.assertTrue(True)  # Sanity check only.
        

if __name__ == '__main__':
    unittest.main()
