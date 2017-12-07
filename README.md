# GitHub Report

Gathers data from GitHub API and exports a dashboard view of branches
and pull requests to a Google Sheets spreadsheet.


## A sample run

    make venv
    source venv/bin/activate
    make init
    python generate_report.py --config klick-genome.config.yml

The klick-genome.config.yml is created per "Configuration" below.

Optionally (runnable in Git Bash):

    ./run_update.sh

# System requirements

* Python 3
* pip
* virtualenv
* make (optional)

You can use a Vagrant box with Python 3 and make installed (e.g.,
https://github.com/jeff-zohrab/devops-box).

## Validation

Check your system requirements are all set up:

    python --version  # should return 3.x.x ...
                      # the Makefile ensures we use python 3.
    pip help          # should work
    virtualenv venv   # should work

# Installation

Clone this repo, and set up the environment:

    make venv
    source venv/bin/activate
    make init

## Configuration

* Copy `config.yml.example` to `config.yml`, and edit the .yml file.
* Copy `github_creds.yml.example` to `github_creds.yml`, and edit the
  .yml file.

Design note: the github creds file is separate from the config file as
the same creds could potentially be used for several repositories.


## Arguments

`generate_report.py` takes various arguments, run it with `-h`:

    usage: generate_report.py [-h] [--config CONFIGFILE] [--creds GITHUBCREDS]
    
    Generate google sheets from github data.
    
    optional arguments:
      -h, --help           show this help message and exit
      --config CONFIGFILE  Path to config file (default is config.yml)
      --creds GITHUBCREDS  Path to github credentials file (default is
                           github_creds.yml)


# Development

Run tests with `make test`
