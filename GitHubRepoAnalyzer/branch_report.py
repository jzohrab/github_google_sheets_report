#!/usr/bin/env python

import yaml
import os
import inspect
import subprocess
import json
import sys
import re
import pandas
import datetime
import pytz

from .utils import TimeUtils

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

    def __init__(self, config, git_repo, reference_date):
        self.config = config
        self.git = git_repo
        self.reference_date = reference_date
        self.have_refreshed_repo = False

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

    def git_date_to_date(self, s):
        d = datetime.datetime.strptime(s, "%Y-%m-%d")
        toronto = pytz.timezone('America/Toronto')
        return pytz.utc.localize(d)

    def git_days_ago(self, s):
        if s is None:
            return None
        d = self.git_date_to_date(s)
        return TimeUtils.human_elapsed_time(self.reference_date, d)

    def git_days_elapsed(self, s):
        if s is None:
            return None
        d = self.git_date_to_date(s)
        return TimeUtils.days_elapsed(self.reference_date, d)

    def get_commits(self, from_branch, to_branch):
        cmd = "git log --date=short --format=\"%cd %an\" {m}..{b}"
        cmd = cmd.format(m=from_branch, b=to_branch)
        return self.git.get_git_cmd_response(cmd)
    
    def get_branch_data(self, reference_branch, branch_name):
        self._refresh_repo()

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

        origin = self.config['localclone']['origin_name']
        return {
            'branch': branch_name.replace("{o}/".format(o=origin), ''),
            'ahead': num_commits_ahead,
            'behind': len(self.get_commits(branch_name, reference_branch)),
            'latest_commit_date': latest_commit,
            'authors': authors or []
            }
    
    def _refresh_repo(self):
        if (self.have_refreshed_repo):
            return

        origin = self.config['localclone']['origin_name']
        if (self.config['localclone']['do_fetch']):
            print("Fetching ...")
            cmd = "git fetch {origin}".format(origin = origin)
            self.git.get_git_cmd_response(cmd)
        if (self.config['localclone']['do_prune']):
            print("Pruning ...")
            cmd = "git remote prune {origin}".format(origin = origin)
            self.git.get_git_cmd_response(cmd)

        self.have_refreshed_repo = True

    def load_data(self):
        dirname = self.config['localclone']['source_dir']
        if (not os.path.exists(dirname) or not os.path.isdir(dirname)):
            raise Exception('missing directory: ' + dirname)

        self._refresh_repo()
        origin = self.config['localclone']['origin_name']
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
        
        data = [self.get_branch_data(reference_branch, b) for b in branches]

        # Note comparing things by string below, as comparing by
        # number seems to magically coerce the values of the hash to
        # decimals (e.g., b['ahead'] = 0.0).
        return [b for b in data if b['ahead'] != '0']

    def load_dataframe(self):
        git_branches = self.load_data()
        branch_columns = [
            'branch',
            'ahead',
            'behind',
            'authors',
            'latest_commit_date'
        ]
        df = pandas.DataFrame(git_branches, columns = branch_columns)
        for f in ['authors']:
            df[f + '_concat'] = list(map(lambda s: ', '.join(s), df[f]))
            df[f + '_count'] = list(map(lambda s: len(s), df[f]))
        df['commit_age_days'] = list(map(lambda d: self.git_days_elapsed(d), df['latest_commit_date']))
        df['commit_days_ago'] = list(map(lambda d: self.git_days_ago(d), df['latest_commit_date']))
        return df


    def load_summary(self):
        def full_branch_name(b):
            origin = self.config['localclone']['origin_name']
            return "{o}/{branch}".format(o=origin, branch=b)
        dev = full_branch_name(self.config['develop_branch'])
        master = full_branch_name(self.config['master_branch'])
        data = self.get_branch_data(dev, master)
        
        ret = {
            'master_ahead_of_develop': data['ahead']
        }
        # ret = [ [ 'master_ahead_of_develop', data['ahead'] ] ]
        return ret

    def load_summary_dataframe(self):
        d = self.load_summary()
        df = pandas.DataFrame(list(d.items()), columns=['key', 'value'])
        return df


if __name__ == '__main__':
    config = None
    with open('config.yml', 'r') as f:
        config = yaml.load(f)
    dirname = config['localclone']['source_dir']
    data = GitBranches(config, GitRepo(dirname), TimeUtils.today()).load_data()
    print(json.dumps(data, indent=2, sort_keys=True))
