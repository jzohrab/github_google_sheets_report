from branch_report import GitBranches, GitRepo
from pull_reqs import GitHubApi, GitHubPullRequests
import yaml
import json
import os

def build_report():
    config = None
    with open('config.yml', 'r') as f:
        config = yaml.load(f)
    dirname = config['localclone']['source_dir']
    data = GitBranches(config, GitRepo(dirname)).load_data()
    print(json.dumps(data, indent=2, sort_keys=True))

    token=os.environ['GITHUB_TOKEN']
    account=os.environ['GITHUB_TOKEN_ACCOUNT']
    if (token is None or token.strip() == ''):
        print("Missing GITHUB_TOKEN env variable")
        sys.exit()
    if (account is None or account.strip() == ''):
        print("Missing GITHUB_TOKEN_ACCOUNT env variable")
        sys.exit()

    api = GitHubApi(account, token)
    pr = GitHubPullRequests(config, api)
    print(json.dumps(pr.load_data(), indent=2, sort_keys=True))

if __name__ == '__main__':
    build_report()
