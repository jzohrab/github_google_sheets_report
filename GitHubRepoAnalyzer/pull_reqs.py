import requests
import json
import sys
import os
import yaml
import subprocess
import pandas
import datetime
import pytz
from requests.auth import HTTPBasicAuth
from .utils import TimeUtils

class GitHubApi:
    """Wrapper class to allow for dependency injection."""

    def __init__(self, account, token):
        def validate(var, name):
            if (var is None or var.strip() == ''):
                print("Missing {name}".format(name=name))
                sys.exit()
        validate(account, 'account')
        self.account = account
        validate(token, 'token')
        self.token = token

    def _hack_write_file(self, url, data):
        """Writes the json returned from the URL to a file.
        Hack, this is not used, but could be used for
        caching, or to regenerate test cases."""
        filename = url.translate({ord(c):'_' for c in "/:."})
        currdir = os.path.dirname(os.path.abspath(__file__))
        cachedir = os.path.join(currdir, 'test_json')
        if not os.path.exists(cachedir):
            os.makedirs(cachedir)
        cachefile = os.path.join(cachedir, filename)
    
        with open(cachefile, 'wt') as out:
            json.dump(data, out, sort_keys=True, indent=4, separators=(',', ': '))

    def _get_json_following_links(self, url, collect_response_json):
        myauth=HTTPBasicAuth(self.account, self.token)
        resp = requests.get(url, auth = myauth)
        j = resp.json()
        if type(j) is dict:
            return [j]

        collect_response_json += resp.json()
        r = requests.head(url, auth = myauth)
        if 'next' in r.links:
            url = r.links['next']['url']
            # print("Getting next url {url}".format(url=url))
            self._get_json_following_links(url, collect_response_json)
        return collect_response_json

    def get_json(self, url):
        """Gets data from the URL, and writes it to a file for subsequent use."""
        ret = self._get_json_following_links(url, [])
        # self._hack_write_file(url, ret)  # Disabling for now.
        return ret


class GitHubPullRequests:
    """Extracts and aggregates GitHub pull requests for a high-level overview."""

    def __init__(self, config, github_api, reference_date):
        self.config = config
        self.github_api = github_api
        self.reference_date = reference_date

    # ---------------------------
    # Branches
    def get_branches(self):
        return {}

    # ---------------------------
    # Pull requests
    def get_pr(self, base_url, number):
        def simplify(pr):
            return {
                'branch': pr['head']['ref'],
                'number': pr['number'],
                'url': pr['html_url'],
                'title': pr['title'],
                'user': pr['user']['login'],
                'updated_at': pr['updated_at'],
                'mergeable': pr['mergeable']
            }
        url = "{base_url}/pulls/{number}".format(base_url=base_url,number=number)
        raw_pr = self.github_api.get_json(url)
        pr = simplify(raw_pr)
    
        pr['status'] = self.get_last_status(raw_pr['statuses_url'])
    
        reviews = self.get_reviews(base_url, number)
        approved = [r['user'] for r in reviews if r['state'] == 'APPROVED']
        declined = [r['user'] for r in reviews if r['state'] == 'CHANGES_REQUESTED']
        pr['approved'] = approved
        pr['declined'] = declined
    
        return pr

    def github_datetime_to_date(self, s):
        """Extracts date from GitHub date, per
        https://stackoverflow.com/questions/18795713/ \
          parse-and-format-the-date-from-the-github-api-in-python"""
        toronto = pytz.timezone('America/Toronto')
        d = pytz.utc.localize(datetime.datetime.strptime(s, "%Y-%m-%dT%H:%M:%SZ"))
        return d.astimezone(toronto)

    def github_days_ago(self, s):
        if s is None:
            return None
        d = self.github_datetime_to_date(s)
        return TimeUtils.human_elapsed_time(self.reference_date, d)

    def github_days_elapsed(self, s):
        if s is None:
            return None
        d = self.github_datetime_to_date(s)
        return TimeUtils.days_elapsed(self.reference_date, d)

    def get_last_status(self, url):
        """Get the last clear success or error status."""
        def simplify(status):
            return {
                'context': status['context'],
                'state': status['state'],
                'description': status['description'],
                'updated_at': status['updated_at']
            }
        aborted_msg = 'The build of this commit was aborted'
        jenkins_context = 'continuous-integration/jenkins/branch'
        statuses = [
            simplify(s)
            for s in self.github_api.get_json(url)
            if ( s['context'] == jenkins_context and
                 s['state'] != 'pending' and
                 s['description'] != aborted_msg
             )
        ]
        if len(statuses) == 0:
            return None
        newlist = sorted(statuses, key=lambda k: k['updated_at'], reverse = True)
        return newlist[0]['state']
    
    def get_reviews(self, base_url, n):
        def simplify(review):
            return {
                'user': review['user']['login'],
                'state': review['state']
            }
        url = "{base_url}/pulls/{number}/reviews".format(base_url=base_url, number=n)
        return [simplify(r) for r in self.github_api.get_json(url)]
    
    
    def load_data(self):
        c = self.config['github']
        api_endpoint = c['api_endpoint']
        org = c['org']
        repo = c['repo']
        base_url = "{api_endpoint}/repos/{org}/{repo}".format(api_endpoint=api_endpoint, org=org,repo=repo)
        base_branch = self.config['develop_branch']
        
        url = "{base_url}/pulls?state=open&base={branch}".format(base_url=base_url, branch=base_branch)
        all_pulls = self.github_api.get_json(url)
        pr_numbers = [pr['number'] for pr in all_pulls]
        
        # GitHub API doesn't return merge status in the regular "pulls" query;
        # have to first get the list of PRs and then get each PR individually.
        prs = [self.get_pr(base_url, n) for n in pr_numbers]
        return prs

    def load_dataframe(self):
        prs = self.load_data()
        pr_columns = [
            'branch',
            'number',
            'title',
            'url',
            'user',
            'updated_at',
            'declined',
            'declined_concat',
            'declined_count',
            'approved',
            'approved_concat',
            'approved_count',
            'mergeable',
            'status'
        ]
        df = pandas.DataFrame(prs, columns = pr_columns)
        for f in ['approved', 'declined']:
            df[f + '_concat'] = list(map(lambda s: ', '.join(s), df[f]))
            df[f + '_count'] = list(map(lambda s: len(s), df[f]))
        df['pr_age_days'] = list(map(lambda d: self.github_days_elapsed(d), df['updated_at']))
        df['github_days_ago'] = list(map(lambda d: self.github_days_ago(d), df['updated_at']))
        return df


if __name__ == '__main__':
    config = None
    with open('config.yml', 'r') as f:
        config = yaml.load(f)

    token=os.environ['GITHUB_TOKEN']
    account=os.environ['GITHUB_TOKEN_ACCOUNT']
    if (token is None or token.strip() == ''):
        print("Missing GITHUB_TOKEN env variable")
        sys.exit()
    if (account is None or account.strip() == ''):
        print("Missing GITHUB_TOKEN_ACCOUNT env variable")
        sys.exit()

    api = GitHubApi(account, token)
    pr = GitHubPullRequests(config, api, datetime.datetime.now())
    # print(json.dumps(pr.load_data(), indent=2, sort_keys=True))

    c = config['github']
    api_endpoint = c['api_endpoint']
    org = c['org']
    repo = c['repo']
    # org = 'KlickInc'
    # repo = 'klick-genome'
    url = "{api_endpoint}/repos/{org}/{repo}/branches".format(api_endpoint=api_endpoint, org=org,repo=repo)
    # print(json.dumps(api.get_json(url), indent=2, sort_keys=True))

    # url = "https://api.github.com/repos/jeff-zohrab/demo_gitflow/commits/08708e05bdcd376b3489a421f9307f65175da924"
    # print(json.dumps(api.get_json(url), indent=2, sort_keys=True))
    
    print(json.dumps(pr.get_branches(), indent=2, sort_keys=True))
