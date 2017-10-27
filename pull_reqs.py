import requests
import json
import sys
import datetime
import os

from requests.auth import HTTPBasicAuth


token=os.environ['GITHUB_TOKEN']
if (token is None or token.strip() == ''):
    print("Missing GITHUB_TOKEN env variable")
    sys.exit()


def get_json(url, params = None):
    """Gets data from the URL, and writes it to a file for subsequent use."""
    filename = url.replace(api_endpoint, '').replace('/', '_')
    currdir = os.path.dirname(os.path.abspath(__file__))
    cachedir = os.path.join(currdir, 'test_json')
    if not os.path.exists(cachedir):
        os.makedirs(cachedir)
    cachefile = os.path.join(cachedir, filename)

    ret = None
    if (os.path.exists(cachefile)):
        with open(cachefile, 'r') as f:
            ret = json.load(f)
    else:
        myauth=HTTPBasicAuth('jeff-zohrab', token)
        resp = requests.get(url, auth = myauth, params = params)
        ret = resp.json()
        with open(cachefile, 'wt') as out:
            json.dump(ret, out, sort_keys=True, indent=4, separators=(',', ': '))
    
    return ret


def github_datetime_to_date(s):
    """Extracts date from GitHub date, per
https://stackoverflow.com/questions/18795713/parse-and-format-the-date-from-the-github-api-in-python"""
    d = datetime.datetime.strptime(s, "%Y-%m-%dT%H:%M:%SZ")
    return d.strftime('%c')


def get_pr(number):
    def simplify(pr):
        return {
            'assignees': pr['assignees'],
            'branch': pr['head']['ref'],
            'number': pr['number'],
            'url': pr['html_url'],
            'requested_reviewers': [u['login'] for u in pr['requested_reviewers']],
            'title': pr['title'],
            'user': pr['user']['login'],
            'updated_at': github_datetime_to_date(pr['updated_at']),
            'statuses_url': pr['statuses_url'],
            'mergeable': pr['mergeable']
        }
    url = "{base_url}/pulls/{number}".format(base_url=base_url,number=number)
    pr = simplify(get_json(url))
    pr['statuses'] = get_statuses(pr['statuses_url'])
    pr['reviews'] = get_reviews(number)
    return pr

def get_statuses(url):
    def simplify(status):
        return {
            'context': status['context'],
            'state': status['state'],
            'description': status['description'],
            'updated_at': github_datetime_to_date(status['updated_at'])
        }
    return [simplify(data) for data in get_json(url)]

def get_reviews(n):
    def simplify(review):
        return {
            'user': review['user']['login'],
            'state': review['state']
        }
    url = "{base_url}/pulls/{number}/reviews".format(base_url=base_url, number=n)
    return [simplify(r) for r in get_json(url)]

def print_data(s, j):
    print('-------------------------------------')
    print(s)
    print(json.dumps(j, indent=2, sort_keys=True))
    print('-------------------------------------')


api_endpoint = 'https://api.github.com'
org = 'jeff-zohrab'
repo = 'demo_gitflow'
base_url = "{api_endpoint}/repos/{org}/{repo}".format(api_endpoint=api_endpoint, org=org,repo=repo)
base_branch = 'develop'
pr_params = {
    'state': 'open',
    'base': base_branch  # if None, returns all PRs
    }

url = "{base_url}/pulls".format(base_url=base_url)
all_pulls = get_json(url, params=pr_params)
pr_numbers = [pr['number'] for pr in all_pulls]

# GitHub API doesn't return merge status in the regular "pulls" query;
# have to first get the list of PRs and then get each PR individually.
prs = [get_pr(n) for n in pr_numbers]


print_data('after_add', prs)

