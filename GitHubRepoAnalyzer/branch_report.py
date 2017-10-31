#!/usr/bin/env python

import yaml
import os
import subprocess
import json

config = None
with open('config.yml', 'r') as f:
    config = yaml.load(f)

dirname = config[':localclone'][':source_dir']
if (not os.path.exists(dirname) or not os.path.isdir(dirname)):
    raise Exception('missing directory: ' + dirname)

os.chdir(dirname)

cmd = "git fetch {origin}".format(origin = config[':localclone'][':origin_name'])
if (config[':localclone'][':do_fetch']):
    print("Fetching ...")
    subprocess.run(cmd, shell=True)
cmd = "git remote prune {origin}".format(origin = config[':localclone'][':origin_name'])
if (config[':localclone'][':do_prune']):
    print("Pruning ...")
    subprocess.run(cmd, shell=True)

branches = []
if (':branches' in config):
    branches = config[':branches']
else:
    cmd = 'git branch -r'
    result = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE)
    rawdata = result.stdout.decode().split("\n")
    branches = [b.strip() for b in rawdata
                if "HEAD" not in b and b != '']

reference_branch = "{origin}/{branch}".format(
    origin=config[':localclone'][':origin_name'],
    branch=config[':develop_branch']
)

branches = [b for b in branches if b != reference_branch]
# print(branches)

def clean_author_name(s):
    """Semi-standardize author names where possible.
    e.g., my sample data had 'first-last' and
    'First Last'.  Convert both of these to 'flast'"""
    ret = s
    if ',' in s:
        (last, first) = s.split(',', 1)
        ret = "{f}{last}".format(f = first[0], last = last)
    if ' ' in s:
        (first, last) = s.split(' ', 1)
        ret = "{f}{last}".format(f = first[0], last = last)
    if '-' in s:
        (first, last) = s.split('-', 1)
        ret = "{f}{last}".format(f = first[0], last = last)
    return ret.lower()

def get_commits(from_branch, to_branch):
    cmd = "git log --date=short --format=\"%cd %an\" {m}..{b}"
    cmd = cmd.format(m=from_branch, b=to_branch)
    result = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE)
    rawdata = result.stdout.decode().split("\n")
    return [c for c in rawdata if c.strip() != '']

def get_branch_data(reference_branch, branch_name):
    commits_ahead = get_commits(reference_branch, branch_name)
    # print(commits_ahead)

    num_commits_ahead = len(commits_ahead)
    latest_commit = None
    authors = None
    if num_commits_ahead > 0:
        latest_commit = max([c.split()[0] for c in commits_ahead])
        authors = list(set(
            [clean_author_name(c.split(' ', 1)[1]) for c in commits_ahead]
        ))
  
    # Expensive ... add if desired.
    # approx_diff_linecount =
    # `git diff #{master}...#{branch_name} | grep ^[+-] | wc -l`.strip

    return {
        'branch_name': branch_name,
        'ahead': num_commits_ahead,
        'behind': len(get_commits(branch_name, reference_branch)),
        'latest_commit_date': latest_commit,
        'authors': authors
        }

def print_data(s, j):
    print('-------------------------------------')
    print(s)
    print(json.dumps(j, indent=2, sort_keys=True))
    print('-------------------------------------')


data = [get_branch_data(reference_branch, b) for b in branches]
print_data('branches', data)
