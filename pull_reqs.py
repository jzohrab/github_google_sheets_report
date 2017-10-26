import requests
import json
import sys
import datetime

from requests.auth import HTTPBasicAuth

token=sys.argv[1]

def github_datetime_to_date(s):
    """Extracts date from GitHub date, per
https://stackoverflow.com/questions/18795713/parse-and-format-the-date-from-the-github-api-in-python"""
    d = datetime.datetime.strptime(s, "%Y-%m-%dT%H:%M:%SZ")
    return d.strftime('%c')

def extract_pr_data(pr):
    ret = {
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
    return ret

def extract_review_data(review):
    ret = {
        'user': review['user']['login'],
        'state': review['state']
    }
    return ret

def extract_jenkins_data(status):
    return {
        'context': status['context'],
        'target_url': status['target_url'],
        'state': status['state'],
        'updated_at': github_datetime_to_date(status['updated_at'])
    }

myauth=HTTPBasicAuth('jeff-zohrab', token)
# resp = requests.get('https://api.github.com/user', auth=myauth)
# print(resp)

api_endpoint = 'https://api.github.com'
org = 'jeff-zohrab'
repo = 'demo_gitflow'
# org = 'klickinc'
# repo = 'klick-genome'

base_url = "{api_endpoint}/repos/{org}/{repo}".format(api_endpoint=api_endpoint, org=org,repo=repo)
base_branch = 'develop'

# TODO: try using session, ref http://docs.python-requests.org/en/master/user/advanced/
# s = requests.Session()
# s.auth = ('user', 'pass')
# s.headers.update({'x-test': 'true'})
# s.get('http://httpbin.org/headers', headers={'x-test2': 'true'})

# GitHub API doesn't return merge status in the regular "pulls" query;
# have to first get the list of PRs and then get each PR individually.

# Get open PR numbers to branch in question
pr_params = {
    'state': 'open',
    'base': base_branch,   # will not be added if base_branch is None.
    }
url = "{base_url}/pulls".format(base_url=base_url)
resp = requests.get(url, auth=myauth, params=pr_params)


# GitHub Pull Request API deals primarily with PR numbers, but we're interested in
# branch names.
branch_to_pr_number = {pr['head']['ref']: pr['number'] for pr in resp.json()}
print(branch_to_pr_number)
pr_numbers = [pr['number'] for pr in resp.json()]
print(pr_numbers)

# TODO try headers, use timezone = America/Toronto
def get_pr(number):
    url = "{base_url}/pulls/{number}".format(base_url=base_url,number=number)
    resp = requests.get(url, auth=myauth)
    return extract_pr_data(resp.json())

def get_statuses(pr):
    url = pr['statuses_url']
    resp = requests.get(url, auth=myauth)
    return [extract_jenkins_data(data) for data in resp.json()]

def get_reviews(n):
    url = "{base_url}/pulls/{number}/reviews".format(base_url=base_url, number=n)
    resp = requests.get(url, auth=myauth)
    return [extract_review_data(r) for r in resp.json()]

def print_data(s, j):
    print('-------------------------------------')
    print(s)
    print(json.dumps(j, indent=2, sort_keys=True))
    print('-------------------------------------')


print_data('raw prs', resp.json())

# Need to call API again to get the branch "mergeable" status.
prs = [get_pr(n) for n in pr_numbers]

def add_status(pr):
    pr['statuses'] = get_statuses(pr)
    return pr
def add_reviews(pr):
    pr['reviews'] = get_reviews(pr['number'])
    return pr

print_data('before_add', prs)

prs = list(map(add_status, prs))  # list() required to serialize data
prs = list(map(add_reviews, prs))

print_data('after_add', prs)

print('QUITTING')
sys.exit()

prs = {n: get_pr(n) for n in pr_numbers}
statuses = {n: get_statuses(prs[n]) for n in pr_numbers}
reviews = {n: get_reviews(n) for n in pr_numbers}

print_data("PRs", prs)
print_data("Statuses", statuses)
print_data("Reviews", reviews)


def lookup_default(dict, n, key):
    if n not in dict:
        return None
    if key not in dict[n]:
        return None
    return dict[n][key]

# Extract final table of data:
# print(branch_to_pr_number)
table = {
    n: {
        'assignees': prs[n]['assignees'],
        'branch': prs[n]['branch'],
        'url': prs[n]['url'],
        'requested_reviewers': prs[n]['requested_reviewers'],
        'title': prs[n]['title'],
        'user': prs[n]['user'],
        'updated_at': prs[n]['updated_at'],
        'mergeable': prs[n]['mergeable'],

        'context': lookup_default(statuses, n, 'context'),
        'target_url': lookup_default(statuses, n, 'target_url'),
        'jenkins_state': lookup_default(statuses, n, 'state'),
        'status_updated_at': lookup_default(statuses, n, 'updated_at'),
        
        'reviewed_by': lookup_default(reviews, n, 'user'),
        'review_state': lookup_default(reviews, n, 'state')
    }
    for n in pr_numbers
}
print(table)

# pr_number = pr_numbers[0]

# resp = requests.get("{base_url}/pulls/{number}".format(base_url=base_url,number=pr_number))
# mypr = resp.json()
# print(json.dumps(extract_pr_data(mypr), indent=2))

# url = mypr['statuses_url']
# resp = requests.get(url, auth=myauth)
# simple_statuses = [extract_jenkins_data(data) for data in resp.json()]
# print("STATUS")
# print(json.dumps(simple_statuses, indent=2))


# # 2469 has requested_reviewers

# # REVIEWS

# url = "{base_url}/pulls/{number}/reviews".format(base_url=base_url, number=pr_number)
# resp = requests.get(url, auth=myauth)
# reviews = [extract_review_data(r) for r in resp.json()]
# print("REVIEWS")
# print(json.dumps(reviews, indent=2))

