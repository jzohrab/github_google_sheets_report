import requests
import json
import sys

from requests.auth import HTTPBasicAuth

token=sys.argv[1]

def extract_pr_data(pr):
    ret = {}
    ret['assignees'] = pr['assignees']
    ret['branch'] = pr['head']['ref']
    ret['url'] = pr['html_url']
    ret['requested_reviewers'] = [u['login'] for u in pr['requested_reviewers']]
    ret['title'] = pr['title']
    ret['user'] = pr['user']['login']
    ret['updated_at'] = pr['updated_at']
    return ret

def extract_review_data(review):
    ret = {}
    ret['user'] = review['user']['login']
    ret['state'] = review['state']
    return ret

myauth=HTTPBasicAuth('jeff-zohrab', token)
# resp = requests.get('https://api.github.com/user', auth=myauth)
# print(resp)

api_endpoint = 'https://api.github.com'
org = 'KlickInc'
repo = 'klick-genome'

base_url = "{api_endpoint}/repos/{org}/{repo}".format(api_endpoint=api_endpoint, org=org,repo=repo)
base_branch = 'develop'

pr_params = {
    'state': 'open',
    'base': base_branch,   # will not be added if base_branch is None.
    }

pr_number = 2469

# Get PR data
url = "{base_url}/pulls".format(base_url=base_url)


resp = requests.get(url, auth=myauth, params=pr_params)
# TODO handle failed auth
prs = resp.json()

with open('sample_pr.txt', 'w') as f:
    f.write(json.dumps(prs[0], indent=2))

pr_numbers = [pr['number'] for pr in prs]
simple_prs = [extract_pr_data(pr) for pr in prs]
print(pr_numbers)
# print(json.dumps(simple_prs, indent=2, sort_keys=True))


# 2469 has requested_reviewers

# REVIEWS
# PR 2464 has completed reviews; pr 2469 returns '[]'
url = "{base_url}/pulls/{number}/reviews".format(base_url=base_url, number=pr_number)
resp = requests.get(url, auth=myauth)
reviews = [extract_review_data(r) for r in resp.json()]
print(json.dumps(reviews, indent=2))

