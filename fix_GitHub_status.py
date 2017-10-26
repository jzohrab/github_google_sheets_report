# fix_GitHub_status
#
# Posts a "success" status to GitHub for the given sha
# if that sha already has a "success" status, as well as
# an "error" status.
#
# Sample call:
#   python <this_script> feature/branch-name-here sha-being-updated
# e.g.
#   python <this_script> origin/feature/1290815_faceted-search-improvements 75e571e21d3a8a7164c0ea107e08c17044e92771

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

if (len(sys.argv) != 3):
    print("Missing sha or branch?")
    sys.exit()

branch=sys.argv[1]
sha=sys.argv[2]
if (sha.strip() == ''):
    print("blank sha?")
    sys.exit()

print("Fixing status for branch {b} at sha {s}".format(b=branch, s=sha))
# sys.exit()

def print_data(s, j):
    print('-------------------------------------')
    print(s)
    print(json.dumps(j, indent=2, sort_keys=True))
    print('-------------------------------------')


myauth=HTTPBasicAuth('jeff-zohrab', token)

api_endpoint = 'https://api.github.com'
org = 'klickinc'
repo = 'klick-genome'

base_url = "{api_endpoint}/repos/{org}/{repo}/commits".format(api_endpoint=api_endpoint, org=org,repo=repo)

url = "{base_url}/{sha}/statuses".format(base_url=base_url, sha=sha)
resp = requests.get(url, auth=myauth)
# print_data('statuses:', resp.json())

good = [status for status in resp.json() if (status['state'] == 'success' and status['context'] == 'continuous-integration/jenkins/branch')]
bad = [status for status in resp.json() if (status['state'] == 'error' and status['context'] == 'continuous-integration/jenkins/branch')]

if (len(good) == 1 and len(bad) == 1):
    print('1 good and 1 bad, create a good to overwrite it')
    bad_status_id = bad[0]['id']
    print("bad id: {b}".format(b=bad_status_id))
    good = good[0]
    posting = {
        "state": good['state'],
        "target_url": good['target_url'],
        "description": good['description'],
        "context": good['context']
    }
    post_url = "{api_endpoint}/repos/{org}/{repo}/statuses/{sha}".format(api_endpoint=api_endpoint, org=org, repo=repo, sha=sha)
    r = requests.post(post_url, data=json.dumps(posting), auth=myauth)
    print("created status {s}".format(s=r.json()['id']))
else:
    print("{g} good and {b} bad, quitting".format(g=len(good), b=len(bad)))

