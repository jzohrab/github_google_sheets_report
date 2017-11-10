from .branch_report import GitBranches, GitRepo
from .pull_reqs import GitHubApi, GitHubPullRequests
from .utils import TimeUtils

import yaml
import json
import os
import datetime
import pytz
import pandas


class GitHubReport:
    def __init__(self, config, git_repo, github_api, reference_date):
        self.config = config
        self.git_repo = git_repo
        self.github_api = github_api
        self.reference_date = reference_date

    def build_dataframe(self):
        gb = GitBranches(self.config, self.git_repo, self.reference_date)
        branch_df = gb.load_dataframe()
        prs = GitHubPullRequests(self.config, self.github_api, self.reference_date)
        pr_df = prs.load_dataframe()
        data = pandas.merge(branch_df, pr_df, how='left', left_on=['branch'], right_on=['branch'])
        data.fillna(value='', inplace=True)

        return data


if __name__ == '__main__':
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

    ghr = GitHubReport(config, git_repo, github_api)
    print(ghr.build_dataframe())
