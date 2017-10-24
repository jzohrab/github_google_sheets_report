#!/usr/bin/env python

import yaml
import os
import subprocess

config = None
with open('config.yml', 'r') as f:
    config = yaml.load(f)

print(config[':do_fetch'])

dirname = config[':source_dir']
print(dirname)
if (not os.path.exists(dirname) or not os.path.isdir(dirname)):
    raise Exception('missing directory: ' + dirname)

os.chdir(dirname)

cmd = "git fetch {origin}".format(origin = config[':origin_name'])
if (config[':do_fetch']):
    print("Fetching ...")
    subprocess.run(cmd, shell=True)
cmd = "git remote prune {origin}".format(origin = config[':origin_name'])
if (config[':do_prune']):
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

print(branches)

def get_branch_data(master, branch_name):
    cmd = "git log --date=short --format=\"%cd %aE\" {m}..{b}"
    cmd = cmd.format(m=master, b=branch_name)
    result = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE)
    rawdata = result.stdout.decode().split("\n")
    print(rawdata)

  #   commits_ahead = log.split("\n").map do |c|
  #   c.split(' ')
  # end
  # num_commits_ahead = commits_ahead.size
  # latest_commit = commits_ahead.map { |d, c| d }.max
  # authors = commits_ahead.map { |d, c| c }.sort.uniq
  # authors = authors.join(', ')
  
  # # Expensive ... add if desired.
  # # approx_diff_linecount = `git diff #{master}...#{branch_name} | grep ^[+-] | wc -l`.strip

  # return [branch_name, num_commits_ahead, latest_commit, authors]

for b in branches:
    print(b)
    get_branch_data('origin/master', b)
