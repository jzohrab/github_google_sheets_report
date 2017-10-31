import requests
import json
import sys
import datetime
import pytz
import os
import yaml
import subprocess
from requests.auth import HTTPBasicAuth


token=os.environ['GITHUB_TOKEN']
if (token is None or token.strip() == ''):
    print("Missing GITHUB_TOKEN env variable")
    sys.exit()


def get_json(url, params = None):
    """Gets data from the URL, and writes it to a file for subsequent use."""
    filename = url.translate({ord(c):'_' for c in "/:."})
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
    toronto = pytz.timezone('America/Toronto')
    d = pytz.utc.localize(datetime.datetime.strptime(s, "%Y-%m-%dT%H:%M:%SZ"))
    toronto_d = d.astimezone(toronto)
    return toronto_d.strftime('%c')


def get_pr(base_url, number):
    def simplify(pr):
        return {
            'branch': pr['head']['ref'],
            'number': pr['number'],
            'url': pr['html_url'],
            'title': pr['title'],
            'user': pr['user']['login'],
            'updated_at': github_datetime_to_date(pr['updated_at']),
            'mergeable': pr['mergeable']
        }
    url = "{base_url}/pulls/{number}".format(base_url=base_url,number=number)
    raw_pr = get_json(url)
    pr = simplify(raw_pr)

    pr['status'] = get_last_status(raw_pr['statuses_url'])

    reviews = get_reviews(base_url, number)
    approved = [r['user'] for r in reviews if r['state'] == 'APPROVED']
    declined = [r['user'] for r in reviews if r['state'] == 'CHANGES_REQUESTED']
    pr['approved'] = approved
    pr['declined'] = declined

    return pr

def get_last_status(url):
    """Get the last clear success or error status."""
    def simplify(status):
        return {
            'context': status['context'],
            'state': status['state'],
            'description': status['description'],
            'updated_at': github_datetime_to_date(status['updated_at'])
        }
    aborted_msg = 'The build of this commit was aborted'
    jenkins_context = 'continuous-integration/jenkins/branch'
    statuses = [
        simplify(s)
        for s in get_json(url)
        if ( s['context'] == jenkins_context and
             s['state'] != 'pending' and
             s['description'] != aborted_msg
         )
    ]
    if len(statuses) == 0:
        return None
    newlist = sorted(statuses, key=lambda k: k['updated_at'], reverse = True)
    return newlist[0]['state']

def get_reviews(base_url, n):
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


def load_data(config):
    c = config[':github']
    api_endpoint = c[':api_endpoint']
    org = c[':org']
    repo = c[':repo']
    base_url = "{api_endpoint}/repos/{org}/{repo}".format(api_endpoint=api_endpoint, org=org,repo=repo)
    base_branch = config[':develop_branch']
    pr_params = {
        'state': 'open',
        'base': base_branch
        }
    
    url = "{base_url}/pulls".format(base_url=base_url)
    all_pulls = get_json(url, params=pr_params)
    pr_numbers = [pr['number'] for pr in all_pulls]
    
    # GitHub API doesn't return merge status in the regular "pulls" query;
    # have to first get the list of PRs and then get each PR individually.
    prs = [get_pr(base_url, n) for n in pr_numbers]
    return prs


if __name__ == '__main__':
    config = None
    with open('config.yml', 'r') as f:
        config = yaml.load(f)
    
    print_data('after_add', load_data(config))

