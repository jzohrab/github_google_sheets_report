#!/usr/bin/env python

import yaml
import os
import inspect
import subprocess
import json
import sys

config = None
with open('config.yml', 'r') as f:
    config = yaml.load(f)


class GitRepo:
    """Wrapper to allow for dependency injection."""
    def __init__(self, directory):
        if (not os.path.exists(directory) or not os.path.isdir(directory)):
            raise Exception('missing directory: ' + directory)
        self.directory = directory

    def get_git_cmd_response(self, cmd):
        """Gets response data from the cmd, and writes it to a file for subsequent use."""
        filename = cmd.translate({ord(c):'_' for c in "/:. \"%=-"})
        currdir = os.getcwd()
        cachedir = os.path.join(currdir, 'test_git')
        if not os.path.exists(cachedir):
            os.makedirs(cachedir)
        cachefile = os.path.join(cachedir, filename)

        currdir = os.getcwd()
        os.chdir(self.directory)
        result = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE)
        os.chdir(currdir)
        rawdata = result.stdout.decode()
    
        if (os.path.exists(cachefile)):
            with open(cachefile, 'r') as f:
                result = f.read()
        else:
            with open(cachefile, 'wt') as out:
                out.write(rawdata)
    
        return [line for line in rawdata.split("\n") if line.strip() != '']


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

def get_commits(git, from_branch, to_branch):
    cmd = "git log --date=short --format=\"%cd %an\" {m}..{b}"
    cmd = cmd.format(m=from_branch, b=to_branch)
    return git.get_git_cmd_response(cmd)

def get_branch_data(git, reference_branch, branch_name, origin):
    commits_ahead = get_commits(git, reference_branch, branch_name)
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
        'branch_name': branch_name.replace("{o}/".format(o=origin), ''),
        'ahead': num_commits_ahead,
        'behind': len(get_commits(git, branch_name, reference_branch)),
        'latest_commit_date': latest_commit,
        'authors': authors
        }


def load_data(config):
    dirname = config[':localclone'][':source_dir']
    if (not os.path.exists(dirname) or not os.path.isdir(dirname)):
        raise Exception('missing directory: ' + dirname)
    git = GitRepo(dirname)

    origin = config[':localclone'][':origin_name']

    if (config[':localclone'][':do_fetch']):
        print("Fetching ...")
        cmd = "git fetch {origin}".format(origin = origin)
        git.get_git_cmd_response(cmd)
    if (config[':localclone'][':do_prune']):
        print("Pruning ...")
        cmd = "git remote prune {origin}".format(origin = origin)
        git.get_git_cmd_response(cmd)
    
    branches = []
    if (':branches' in config):
        branches = config[':branches']
    else:
        cmd = 'git branch -r'
        rawdata = git.get_git_cmd_response(cmd)
        # result = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE)
        # rawdata = result.stdout.decode().split("\n")
        branches = [b.strip() for b in rawdata
                    if "HEAD" not in b and b != '' and b.strip().startswith(origin)]
    
    reference_branch = "{origin}/{branch}".format(
        origin=origin,
        branch=config[':develop_branch']
    )
    
    branches = [b for b in branches if b != reference_branch]
    # print(branches)
    
    data = [get_branch_data(git, reference_branch, b, origin) for b in branches]
    return data


if __name__ == '__main__':
    print(json.dumps(load_data(config), indent=2, sort_keys=True))
