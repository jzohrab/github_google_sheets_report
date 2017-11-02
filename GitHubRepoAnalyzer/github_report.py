from .branch_report import GitBranches, GitRepo
from .pull_reqs import GitHubApi, GitHubPullRequests
import yaml
import json
import os

class GitHubReport:
    def __init__(self, config, git_repo, github_api):
        self.config = config
        self.git_repo = git_repo
        self.github_api = github_api

    def build_report(self):
        data = GitBranches(self.config, self.git_repo).load_data()
        print(json.dumps(data, indent=2, sort_keys=True))

        pr = GitHubPullRequests(self.config, self.github_api)
        print(json.dumps(pr.load_data(), indent=2, sort_keys=True))


def build_report():
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
    ghr.build_report()

if __name__ == '__main__':
    build_report()
