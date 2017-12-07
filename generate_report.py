from GitHubReport import report

import argparse
import yaml


def parse_arguments():
    """Get command line args."""
    parser = argparse.ArgumentParser(description='Generate google sheets from github data.')
    parser.add_argument(
        '--config', dest='configfile', default='config.yml',
        help='Path to config file (default is config.yml)'
    )
    parser.add_argument(
        '--creds', dest='githubcreds', default='github_creds.yml',
        help='Path to github credentials file (default is github_creds.yml)'
    )
    args = parser.parse_args()
    return args

def get_yml(yml_path):
    with open(yml_path, 'r') as f:
        return yaml.load(f)


args = parse_arguments()
config = get_yml(args.configfile)
github_creds = get_yml(args.githubcreds)
report.create_report(config, github_creds)
