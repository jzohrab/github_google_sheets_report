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
    ret['statuses_url'] = pr['statuses_url']
    ret['mergeable'] = pr['mergeable']
    return ret

def extract_review_data(review):
    ret = {}
    ret['user'] = review['user']['login']
    ret['state'] = review['state']
    return ret

def extract_jenkins_data(status):
    return {
        "context": status['context'],
        "target_url": status['target_url'],
        "state": status['state'],
        "updated_at": status['updated_at']
    }

myauth=HTTPBasicAuth('jeff-zohrab', token)
# resp = requests.get('https://api.github.com/user', auth=myauth)
# print(resp)

api_endpoint = 'https://api.github.com'
org = 'jeff-zohrab'
repo = 'demo_gitflow'

base_url = "{api_endpoint}/repos/{org}/{repo}".format(api_endpoint=api_endpoint, org=org,repo=repo)
base_branch = 'develop'

# GitHub API doesn't return merge status in the regular "pulls" query;
# have to first get the list of PRs and then get each PR individually.

# Get open PR numbers to branch in question
pr_params = {
    'state': 'open',
    'base': base_branch,   # will not be added if base_branch is None.
    }
url = "{base_url}/pulls".format(base_url=base_url)
resp = requests.get(url, auth=myauth, params=pr_params)
pr_numbers = [pr['number'] for pr in resp.json()]
print(pr_numbers)

def get_pr(number):
    resp = requests.get("{base_url}/pulls/{number}".format(base_url=base_url,number=number))
    return extract_pr_data(resp.json())

def get_statuses(pr):
    url = pr['statuses_url']
    resp = requests.get(url)
    return [extract_jenkins_data(data) for data in resp.json()]

def get_reviews(n):
    url = "{base_url}/pulls/{number}/reviews".format(base_url=base_url, number=n)
    resp = requests.get(url, auth=myauth)
    return [extract_review_data(r) for r in resp.json()]

prs = {n: get_pr(n) for n in pr_numbers}
statuses = {n: get_statuses(prs[n]) for n in pr_numbers}
reviews = {n: get_reviews(n) for n in pr_numbers}

print(prs)
print(statuses)
print(reviews)


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

