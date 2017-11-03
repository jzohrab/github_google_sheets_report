from .branch_report import GitBranches, GitRepo
from .pull_reqs import GitHubApi, GitHubPullRequests
import yaml
import json
import os
import datetime
import pandas

class TimeUtils:
    @staticmethod
    def human_elapsed_time(reference_date, d):
        if (d > reference_date):
           return "Some time in the future (?)"
        s = int((reference_date - d).total_seconds())
        # if s < 0:
        #     return "Some time in the future (?)"
        if s == 0:
            return "Just now"
        minute = 60
        hour = 60 * minute
        day = 24 * hour
        month = 30 * day

        def msg(s, unit_size, unit_name):
            count = s // unit_size
            pluralized = unit_name
            if count > 1:
               pluralized += 's'
            return "{n} {units} ago".format(n = count, units = pluralized)
        if s < minute:  return "< 1 minute ago"
        if s < hour:    return msg(s, minute, 'minute')
        if s < day:     return msg(s, hour, 'hour')
        if s < month:   return msg(s, day, 'day')
        if s < 2*month: return "1 month ago"
        if s < 7*month: return "{n} months ago".format(n = s // month)
        return "> 6 months ago"


class GitHubReport:
    def __init__(self, config, git_repo, github_api, reference_date = datetime.datetime.now):
        self.config = config
        self.git_repo = git_repo
        self.github_api = github_api
        self.reference_date = reference_date

        
    def github_datetime_to_date(self, s):
        """Extracts date from GitHub date, per
        https://stackoverflow.com/questions/18795713/ \
          parse-and-format-the-date-from-the-github-api-in-python"""
        toronto = pytz.timezone('America/Toronto')
        d = pytz.utc.localize(datetime.datetime.strptime(s, "%Y-%m-%dT%H:%M:%SZ"))
        return d.astimezone(toronto)

    def git_date_to_date(self, s):
        return datetime.datetime.strptime(s, "%Y-%m-%d")
    
    def build_report(self):
        git_branches = GitBranches(self.config, self.git_repo).load_data()
        prs = GitHubPullRequests(self.config, self.github_api).load_data()
        branch_dict = { b['branch']:b for b in git_branches }
        pr_dict = { pr['branch']:pr for pr in prs }

        full = {branch_name: dict(list(branch_dict[branch_name].items()) + list(pr_dict.get(branch_name, {}).items())) for branch_name, data in branch_dict.items()}
        data = list(full.values())
        def final_data(d):
            updates = {}
            for field in ['authors', 'approved', 'declined']:
                a = d.get(field, []) or []
                updates[field + '_concat'] = ', '.join(a)
                updates[field + '_count'] = len(a)
            d = dict(list(d.items()) + list(updates.items()))
            return d
        data = list(map(final_data, data))
        return data

    def build_dataframe(self):
        columns = [
            'branch',
            'ahead',
            'behind',
            'authors',
            'authors_concat',
            'authors_count',
            'latest_commit_date',
            
            'number',
            'title',
            'url',
            'user',
            'updated_at',
            
            'declined',
            'declined_concat',
            'declined_count',
            'approved',
            'approved_concat',
            'approved_count',
            'mergeable',
            'status'
        ]
        df = pandas.DataFrame(self.build_report(), columns=columns)
        df.fillna(value='', inplace=True)
        return df

    def build_dataframe_v2(self):
        git_branches = GitBranches(self.config, self.git_repo).load_data()
        branch_columns = [
            'branch',
            'ahead',
            'behind',
            'authors',
            'latest_commit_date'
        ]
        branch_df = pandas.DataFrame(git_branches, columns = branch_columns)
        for f in ['authors']:
            branch_df[f + '_concat'] = list(map(lambda s: ', '.join(s), branch_df[f]))
            branch_df[f + '_count'] = list(map(lambda s: len(s), branch_df[f]))

        prs = GitHubPullRequests(self.config, self.github_api).load_data()
        pr_columns = [
            'branch',
            'number',
            'title',
            'url',
            'user',
            'updated_at',
            
            'declined',
            'declined_concat',
            'declined_count',
            'approved',
            'approved_concat',
            'approved_count',
            'mergeable',
            'status'
        ]
        pr_df = pandas.DataFrame(prs, columns = pr_columns)
        for f in ['approved', 'declined']:
            pr_df[f + '_concat'] = list(map(lambda s: ', '.join(s), pr_df[f]))
            pr_df[f + '_count'] = list(map(lambda s: len(s), pr_df[f]))

        data = pandas.merge(branch_df, pr_df, how='left', left_on=['branch'], right_on=['branch'])
        data.fillna(value='', inplace=True)

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
