from GitHubRepoAnalyzer.pull_reqs import GitHubApi, GitHubPullRequests

import yaml
import json
import os
import datetime
import pytz
import pandas
import pygsheets

def create_report():
    def get_valid_env_var(name):
        ret = os.environ[name]
        if (ret is None or ret.strip() == ''):
            print("Missing {name} env variable".format(name = name))
            sys.exit()
        return ret

    config = None
    with open('config.yml', 'r') as f:
        config = yaml.load(f)

    token = get_valid_env_var('GITHUB_TOKEN')
    account = get_valid_env_var('GITHUB_TOKEN_ACCOUNT')
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


if __name__ == '__main__':
    create_report()
