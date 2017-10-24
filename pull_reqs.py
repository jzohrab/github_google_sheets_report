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

base = 'https://api.github.com'


pr_number = 2469

# Get PR data
url = "{base}/repos/KlickInc/klick-genome/pulls?base=develop&state=open".format(base=base)
resp = requests.get(url, auth=myauth)
# TODO handle failed auth
prs = resp.json()
prs = [extract_pr_data(pr) for pr in prs if pr['number'] == pr_number]
print(json.dumps(prs, indent=2, sort_keys=True))


# 2469 has requested_reviewers

# REVIEWS
# PR 2464 has completed reviews; pr 2469 returns '[]'
url = "{base}/repos/KlickInc/klick-genome/pulls/{number}/reviews".format(base=base, number=pr_number)
resp = requests.get(url, auth=myauth)
reviews = [extract_review_data(r) for r in resp.json()]
print(json.dumps(reviews, indent=2))

