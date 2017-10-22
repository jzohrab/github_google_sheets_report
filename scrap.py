#!/usr/bin/env python

import yaml

config = None
with open('config.yml', 'r') as f:
    config = yaml.load(f)

print(config[':do_fetch'])
print(config[':sample_branches'])
