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
        git_branches = GitBranches(self.config, self.git_repo).load_data()
        prs = GitHubPullRequests(self.config, self.github_api).load_data()
        branch_dict = { b['branch_name']:b for b in git_branches }
        pr_dict = { pr['branch']:pr for pr in prs }

        full = {branch_name: dict(list(branch_dict[branch_name].items()) + list(pr_dict.get(branch_name, {}).items())) for branch_name, data in branch_dict.items()}
        data = list(full.values())
        # print(data)
        # return
        def final_data(d):
            updates = {}
            for field in ['authors', 'approved', 'declined']:
                a = d.get(field, []) or []
                updates[field + '_concat'] = ', '.join(a)
                updates[field + '_count'] = len(a)
            # print(updates)
            # def array(key):
            #     return d.get(key, []) or []
            # def get_joined(key):
            #     return ', '.join(d.get(key, []) or [])
            # d['authors'] = get_joined('authors')
            # d['approved'] = get_joined('approved')
            # d['declined'] = get_joined('declined')
            d = dict(list(d.items()) + list(updates.items()))
            # print(d)
            return d
        data = list(map(final_data, data))
        return data

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
