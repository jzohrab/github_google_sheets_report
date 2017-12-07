from .github import GitHubApi, GitHubReportSource

import argparse
import yaml
import json
import os
import datetime
import pytz
import pandas
import pygsheets


def _read_staff_list(config):
    ret = []
    gc = pygsheets.authorize()
    sh = gc.open(config['team_list_sheet_filename'])
    wks = sh.worksheet_by_title('staff')
    df = wks.get_as_df()
    headings = ['canonical_name', 'git_email', 'github_user', 'slack_username', 'team']
    for index, row in df.iterrows():
        entry = {h: row[h] for h in headings}
        ret.append(entry)
    # print(df)
    # print(ret)
    return ret

def _get_staff_map(config, from_field, to_field):
    staff = _read_staff_list(config)
    ret = {m[from_field]: m[to_field] for m in staff if m[from_field] != ''}
    return pandas.DataFrame(list(ret.items()), columns=[from_field, to_field])

def git_author_to_team_map(config):
    return _get_staff_map(config, 'git_email', 'team')

def github_user_to_team_map(config):
    return _get_staff_map(config, 'github_user', 'team')

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

    print('Authorizing google sheets')
    gc = pygsheets.authorize()
    sh = gc.open(config['google_sheets_filename'])

    def dump_dataframe(title, df):
        wks = sh.worksheet_by_title(title)
        wks.clear()
        wks.set_dataframe(df,(1,1))

    print('Creating report:')
    report_source = GitHubReportSource(config, github_api, reference_date)

    print('  Branches')
    df = report_source.get_branches_dataframe().sort_values(by='last_commit_age', ascending=False)
    data = pandas.merge(df, git_author_to_team_map(config), how='left', left_on=['author'], right_on=['git_email'])
    data.fillna(value='', inplace=True)
    dump_dataframe('branches', data)

    print('  Pull requests')
    df = report_source.get_pull_requests_dataframe().sort_values(by='pr_age_days', ascending=False)
    data = pandas.merge(df, github_user_to_team_map(config), how='left', left_on=['user'], right_on=['github_user'])
    data.fillna(value='', inplace=True)
    dump_dataframe('pull_reqs', data)

    print('Done.')
