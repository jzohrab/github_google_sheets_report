#!/usr/bin/env python

import yaml
import os

config = None
with open('config.yml', 'r') as f:
    config = yaml.load(f)

print(config[':do_fetch'])
# print(config[':sample_branches'])

dirname = config[':source_dir']
print(dirname)
print(os.path.exists(dirname))
print(os.path.isdir(dirname))
