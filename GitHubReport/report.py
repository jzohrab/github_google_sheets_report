from .github import GitHubApi, GitHubReportSource

import argparse
import yaml
import json
import os
import datetime
import pytz
import pandas
import pygsheets
import sys

def _read_staff_list(sh):
    ret = []
    wks = sh.worksheet_by_title('team_list')
    df = wks.get_as_df()
    headings = ['name', 'git_email', 'github_user', 'slack_username', 'team']
    for index, row in df.iterrows():
        entry = {h: row[h] for h in headings}
        ret.append(entry)
    return ret

def _get_staff_map(sh, from_field, to_field):
    staff = _read_staff_list(sh)
    ret = {m[from_field]: m[to_field] for m in staff if m[from_field] != ''}
    return pandas.DataFrame(list(ret.items()), columns=[from_field, to_field])

def git_author_to_team_map(sh):
    return _get_staff_map(sh, 'git_email', 'team')

def github_user_to_team_map(sh):
    return _get_staff_map(sh, 'github_user', 'team')

def _get_on_hold_branches(sh):
    wks = sh.worksheet_by_title('on_hold_branches')
    ret = []
    df = wks.get_as_df()
    for index, row in df.iterrows():
        ret.append(row['branch'])
    return ret

def _validate_google_sheets(sh):
    """Throws an exception if missing any sheets."""
    for tabname in ['on_hold_branches', 'team_list', 'branches', 'pull_reqs']:
        print("  {t}".format(t=tabname))
        wks = sh.worksheet_by_title(tabname)

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

    print('Start.')
    print('Authorizing google sheets')
    sys.stdout.flush()
    gc = pygsheets.authorize(no_cache=True)
    sheetname = config['google_sheets_filename']
    sh = gc.open(sheetname)

    print("Validating structure of {sheetname}".format(sheetname = sheetname))
    _validate_google_sheets(sh)

    print('Reading branches to exclude')
    exclude_branches = _get_on_hold_branches(sh)

    def dump_dataframe(title, df):
        wks = sh.worksheet_by_title(title)
        wks.clear()
        wks.set_dataframe(df,(1,1))

    print('Creating report:')
    sys.stdout.flush()
    report_source = GitHubReportSource(config, github_api, reference_date)

    print('  Branches')
    sys.stdout.flush()
    df = report_source.get_branches_dataframe().sort_values(by='last_commit_age', ascending=False)
    df = df[~df.branch.isin(exclude_branches)]
    data = pandas.merge(df, git_author_to_team_map(sh), how='left', left_on=['author'], right_on=['git_email'])
    data.fillna(value='', inplace=True)
    dump_dataframe('branches', data)

    print('  Pull requests')
    sys.stdout.flush()
    df = report_source.get_pull_requests_dataframe().sort_values(by='pr_age_days', ascending=False)
    data = pandas.merge(df, github_user_to_team_map(sh), how='left', left_on=['user'], right_on=['github_user'])
    data.fillna(value='', inplace=True)
    dump_dataframe('pull_reqs', data)

    print('Done.')
    sys.stdout.flush()
