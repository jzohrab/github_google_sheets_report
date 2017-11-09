#!/usr/bin/env python

import yaml
import os
import inspect
import subprocess
import json
import sys
import re

class GitRepo:
    """Wrapper to allow for dependency injection."""
    def __init__(self, directory):
        if (not os.path.exists(directory) or not os.path.isdir(directory)):
            raise Exception('missing directory: ' + directory)
        self.directory = directory

    def _hack_write_file(self, cmd, data):
        """Writes the json returned from the cmd to a file.
        Hack, this is not used, but could be used for
        caching, or to regenerate test cases."""
        filename = cmd.translate({ord(c):'_' for c in "/:. \"%=-"})
        currdir = os.path.dirname(os.path.abspath(__file__))
        cachedir = os.path.join(currdir, 'test_json')
        if not os.path.exists(cachedir):
            os.makedirs(cachedir)
        f = os.path.join(cachedir, filename)
        with open(f, 'wt') as out:
            out.dump(data)

    def get_git_cmd_response(self, cmd):
        """Gets response data from the cmd, and writes it to a file for subsequent use."""
        currdir = os.getcwd()
        os.chdir(self.directory)
        result = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE)
        os.chdir(currdir)
        rawdata = result.stdout.decode()
        # self._hack_write_file(cmd, rawdata)
        return [line for line in rawdata.split("\n") if line.strip() != '']


class GitBranches:
    """Extracts and aggregates Git branch data for a high-level overview."""

    def __init__(self, config, git_repo):
        self.config = config
        self.git = git_repo
    
    def clean_author_name(self, s):
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
    
    def get_commits(self, from_branch, to_branch):
        cmd = "git log --date=short --format=\"%cd %an\" {m}..{b}"
        cmd = cmd.format(m=from_branch, b=to_branch)
        return self.git.get_git_cmd_response(cmd)
    
    def get_branch_data(self, reference_branch, branch_name, origin):
        commits_ahead = self.get_commits(reference_branch, branch_name)
        # print(commits_ahead)
    
        num_commits_ahead = len(commits_ahead)
        latest_commit = None
        authors = None
        if num_commits_ahead > 0:
            latest_commit = max([c.split()[0] for c in commits_ahead])
            authors = list(set(
                [self.clean_author_name(c.split(' ', 1)[1]) for c in commits_ahead]
            ))
      
        # Expensive ... add if desired.
        # approx_diff_linecount =
        # `git diff #{master}...#{branch_name} | grep ^[+-] | wc -l`.strip
    
        return {
            'branch': branch_name.replace("{o}/".format(o=origin), ''),
            'ahead': num_commits_ahead,
            'behind': len(self.get_commits(branch_name, reference_branch)),
            'latest_commit_date': latest_commit,
            'authors': authors or []
            }
    
    
    def load_data(self):
        dirname = self.config['localclone']['source_dir']
        if (not os.path.exists(dirname) or not os.path.isdir(dirname)):
            raise Exception('missing directory: ' + dirname)
    
        origin = self.config['localclone']['origin_name']
    
        if (self.config['localclone']['do_fetch']):
            print("Fetching ...")
            cmd = "git fetch {origin}".format(origin = origin)
            self.git.get_git_cmd_response(cmd)
        if (self.config['localclone']['do_prune']):
            print("Pruning ...")
            cmd = "git remote prune {origin}".format(origin = origin)
            self.git.get_git_cmd_response(cmd)
        
        branches = []
        if ('branches' in self.config):
            branches = self.config['branches']
        else:
            cmd = 'git branch -r'
            rawdata = self.git.get_git_cmd_response(cmd)
            # result = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE)
            # rawdata = result.stdout.decode().split("\n")
            branches = [b.strip() for b in rawdata
                        if "HEAD" not in b and b != '' and b.strip().startswith(origin)]
        
        reference_branch = "{origin}/{branch}".format(
            origin=origin,
            branch=self.config['develop_branch']
        )

        branch_regex = [ "{origin}/{r}".format(origin=origin, r=filter) for filter in self.config['include'] ]
        combined = "(" + ")|(".join(branch_regex) + ")"

        branches = [b for b in branches if b != reference_branch and re.match(combined, b)]
        # print(branches)
        
        data = [self.get_branch_data(reference_branch, b, origin) for b in branches]
        return data


if __name__ == '__main__':
    config = None
    with open('config.yml', 'r') as f:
        config = yaml.load(f)
    dirname = config['localclone']['source_dir']
    data = GitBranches(config, GitRepo(dirname)).load_data()
    print(json.dumps(data, indent=2, sort_keys=True))
