import unittest
import os
import json
import yaml


class FakeGitHubApi:
    """Fake class implementing the GitHubApi API"""
    def get_json(self, url):
        """Gets data from file."""
        currdir = os.path.dirname(os.path.abspath(__file__))
        cachedir = os.path.join(currdir, 'data', 'fake_github_api_json')
        filename = url.translate({ord(c):'_' for c in "/:.?&="})
        filename = filename.replace('https___api_github_com_repos_jeff-zohrab_demo_gitflow_', '')
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
