from GitHubRepoAnalyzer.pull_reqs import GitHubApi, GitHubPullRequests

import argparse
import yaml
import json
import os
import datetime
import pytz
import pandas
import pygsheets


def create_report(config, github_creds):
    def get_valid_env_var(name):
        ret = os.environ[name]
        if (ret is None or ret.strip() == ''):
            print("Missing {name} env variable".format(name = name))
            sys.exit()
        return ret

    account = github_creds['account_name']
    token = github_creds['github_token']
    github_api = GitHubApi(account, token)

    reference_date = datetime.datetime.now()
    toronto = pytz.timezone('America/Toronto')
    reference_date = pytz.utc.localize(reference_date)

    gc = pygsheets.authorize()
    sh = gc.open(config['google_sheets_filename'])

    def dump_dataframe(title, df):
        wks = sh.worksheet_by_title(title)
        wks.clear()
        wks.set_dataframe(df,(1,1))

    prs = GitHubPullRequests(config, github_api, reference_date)

    df = prs.build_full_report()
    dump_dataframe('raw_data_full', df)

    df = prs.get_branches_dataframe().sort_values(by='last_commit_age', ascending=False)
    dump_dataframe('branches', df)

    df = prs.load_dataframe().sort_values(by='pr_age_days', ascending=False)
    dump_dataframe('pull_reqs', df)


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

if __name__ == '__main__':
    args = parse_arguments()

    def get_yml(yml_path):
        with open(yml_path, 'r') as f:
            return yaml.load(f)

    config = get_yml(args.configfile)
    github_creds = get_yml(args.githubcreds)

    create_report(config, github_creds)
