import requests
import json
import sys
import os
import yaml
import re
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
        """Gets data from the URL.  If is array, checks for pagination."""
        myauth=HTTPBasicAuth(self.account, self.token)
        resp = requests.get(url, auth = myauth)
        j = resp.json()

        # If it's an array, it might be paginated.
        if type(j) is not dict:
            r = requests.head(url, auth = myauth)
            if 'next' in r.links:
                url = r.links['next']['url']
                # print("Getting next url {url}".format(url=url))
                self._get_json_following_links(url, j)

        # self._hack_write_file(url, j)  # Disabling for now.
        return j


class GitHubPullRequests:
    """Extracts and aggregates GitHub pull requests for a high-level overview."""

    def __init__(self, config, github_api, reference_date):
        self.config = config
        self.github_api = github_api
        self.reference_date = reference_date

    # ---------------------------

    def get_branch_data(self, branch_name):
        api_endpoint = self.config['api_endpoint']
        org = self.config['org']
        repo = self.config['repo']
        url = "{api_endpoint}/repos/{org}/{repo}/branches/{b}".format(
            api_endpoint=api_endpoint, org=org, repo=repo, b = branch_name)
        d = self.github_api.get_json(url)
        c = d['commit']['commit']
        status_url = "{api_endpoint}/repos/{org}/{repo}/commits/{ref}/statuses".format(
            api_endpoint=api_endpoint, org=org, repo=repo, ref = d['commit']['sha'])
        status = self.get_last_status(status_url)

        commit_date = c['committer']['date']
        age_days = self.github_days_elapsed(commit_date)
        days_ago = self.github_days_ago(commit_date)
        
        return {
            'branch': d['name'],
            'sha': d['commit']['sha'],
            'last_commit_date': self.github_datetime_to_date(commit_date).strftime('%Y-%m-%d'),
            'last_commit_age': age_days,
            'last_commit_days_ago': days_ago,
            'author': c['author']['email'],
            'status': status  
        }


    # Branches
    def get_branches(self):
        api_endpoint = self.config['api_endpoint']
        org = self.config['org']
        repo = self.config['repo']
        url = "{api_endpoint}/repos/{org}/{repo}/branches".format(api_endpoint=api_endpoint, org=org,repo=repo)
        branches = [b['name'] for b in self.github_api.get_json(url)]

        branch_regex = [ f for f in self.config['include'] ]
        combined = "(" + ")|(".join(branch_regex) + ")"

        reference_branch = self.config['develop_branch']
        branches = [b for b in branches if b != reference_branch and re.match(combined, b)]
        
        data = [self.get_branch_data(b) for b in branches]

        return data
        # Note comparing things by string below, as comparing by
        # number seems to magically coerce the values of the hash to
        # decimals (e.g., b['ahead'] = 0.0).
        # return [b for b in data if b['ahead'] != '0']

    def get_branches_dataframe(self):
        cols = [
            'branch',
            'last_commit_date',
            'last_commit_age',
            'author',
            'status'
        ]
        df = pandas.DataFrame(self.get_branches(), columns = cols)
        df.fillna(value='', inplace=True)
        return df


    # ---------------------------
    # Pull requests
    def get_pr(self, base_url, number):
        def fix_boolean(b):
            if b:
                return 'yes'
            return 'no'
        def simplify(pr):
            return {
                'branch': pr['head']['ref'],
                'number': pr['number'],
                'url': pr['html_url'],
                'title': pr['title'],
                'user': pr['user']['login'],
                'updated_at': pr['updated_at'],
                'mergeable': fix_boolean(pr['mergeable'])
            }
        url = "{base_url}/pulls/{number}".format(base_url=base_url,number=number)
        raw_pr = self.github_api.get_json(url)
        pr = simplify(raw_pr)
    
        pr['status'] = self.get_last_status(raw_pr['statuses_url'])
        pr['pr_age_days'] = self.github_days_elapsed(pr['updated_at'])
        pr['github_days_ago'] = self.github_days_ago(pr['updated_at'])

        reviews = self.get_reviews(base_url, number)
        approved = [r['user'] for r in reviews if r['state'] == 'APPROVED']
        declined = [r['user'] for r in reviews if r['state'] == 'CHANGES_REQUESTED']
        def add_review_stats(pr, key, userlist):
            pr[key] = userlist
            pr[key + '_concat'] = ', '.join(userlist)
            pr[key + '_count'] = len(userlist)
        add_review_stats(pr, 'approved', approved)
        add_review_stats(pr, 'declined', declined)

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
        api_endpoint = self.config['api_endpoint']
        org = self.config['org']
        repo = self.config['repo']
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
        prs = pandas.DataFrame(self.load_data())

        pr_columns = [
            'branch',
            'number',
            'title',
            'url',
            'user',
            'updated_at',
            'pr_age_days',
            'declined_concat',
            'declined_count',
            'approved_concat',
            'approved_count',
            'mergeable',
            'status'
        ]
        df = pandas.DataFrame(prs, columns = pr_columns)
        df.fillna(value='', inplace=True)
        return df


    def build_full_report(self):
        cols = [
            'branch',
            'number',
            'title',
            'url',
            'user',
            'updated_at',
            'pr_age_days',
            'approved_count',
            'declined_count',
            'mergeable',
        ]
        pr_df = self.load_dataframe()[cols]

        cols = [
            'branch',
            'author',
            'last_commit_date',
            'last_commit_age',
            'status'
        ]
        branch_df = self.get_branches_dataframe()[cols]
        data = pandas.merge(branch_df, pr_df, how='left', left_on=['branch'], right_on=['branch'])
        data.fillna(value='', inplace=True)

        return data


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

    api_endpoint = config['api_endpoint']
    org = config['org']
    repo = config['repo']
    # org = 'KlickInc'
    # repo = 'klick-genome'
    # url = "{api_endpoint}/repos/{org}/{repo}/branches".format(api_endpoint=api_endpoint, org=org,repo=repo)
    # print(json.dumps(api.get_json(url), indent=2, sort_keys=True))

    # url = "https://api.github.com/repos/jeff-zohrab/demo_gitflow/commits/08708e05bdcd376b3489a421f9307f65175da924"
    # print(json.dumps(api.get_json(url), indent=2, sort_keys=True))
    
    print(json.dumps(pr.get_branches(), indent=2, sort_keys=True))
