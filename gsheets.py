from GitHubRepoAnalyzer.branch_report import GitBranches, GitRepo
from GitHubRepoAnalyzer.pull_reqs import GitHubApi, GitHubPullRequests
from GitHubRepoAnalyzer.github_report import GitHubReport

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

    git_repo = GitRepo(config['localclone']['source_dir'])

    token = get_valid_env_var('GITHUB_TOKEN')
    account = get_valid_env_var('GITHUB_TOKEN_ACCOUNT')
    github_api = GitHubApi(account, token)

    reference_date = datetime.datetime.now()
    toronto = pytz.timezone('America/Toronto')
    reference_date = pytz.utc.localize(reference_date)

    ghr = GitHubReport(config, git_repo, github_api, reference_date)
    df = ghr.build_dataframe()
    cols = [
        'branch',
        'behind',
        'ahead',
        'authors_concat',
        'latest_commit_date',
        'commit_age_days',
        'commit_days_ago',
        'number',
        'title',
        'url',
        'user',
        'updated_at',
        'pr_age_days',
        'github_days_ago',
        'approved_count',
        'declined_count',
        'mergeable',
        'status',
    ]
    output_df = df[cols]
    gc = pygsheets.authorize()
    sh = gc.open('klick-genome repo')

    def dump_dataframe(title, df):
        wks = sh.worksheet_by_title(title)
        wks.clear()
        wks.set_dataframe(df,(1,1))

    gb = GitBranches(config, git_repo, reference_date)
    prs = GitHubPullRequests(config, github_api, reference_date)

    dump_dataframe('raw_data_full', output_df)
    dump_dataframe('raw_data_branches', gb.load_dataframe())
    dump_dataframe('raw_data_pull_requests', prs.load_dataframe())


if __name__ == '__main__':
    create_report()
