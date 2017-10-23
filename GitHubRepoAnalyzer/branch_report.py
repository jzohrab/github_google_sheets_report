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
