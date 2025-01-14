import os
from datetime import datetime
import pytz
import requests
from dotenv import load_dotenv

from github_connection.datetime_utils import get_target_date, get_timezone_from_location
from utils import fetch, graphql_fetch

load_dotenv()
access_key = os.getenv("GIT_ACCESS_KEY")

req_headers = {
    'Authorization': 'token ' + access_key
}

gql_github = 'https://api.github.com/graphql'

class GitUser:
    timezone = None
    range_date = None
    def __init__(self, name):
        self.name = name
        self.set_user_timezone()

    def set_user_timezone(self):
        self.timezone = get_user_timezone(self.name)

def get_user_timezone(user: str):
    try:
        url = f'https://api.github.com/users/{user}'
        fetch_user = fetch(url)
        timezone = get_timezone_from_location(fetch_user['location'])
        return timezone
    except requests.exceptions.RequestException as e:
        print(e)
        return pytz.timezone('America/New_York')


def get_pulls_query(author, start_date, end_date):
    return f"""
    query {{
        search (query: "is:pr author:{author} updated:{start_date}..{end_date}", type: ISSUE, first: 20) {{
            edges {{
                node {{
                    ... on PullRequest {{
                        title
                        commits (first: 50) {{
                            edges {{
                                node {{
                                    commit {{
                                        message
                                        authoredDate
                                    }}
                                }}
                            }}
                        }}
                    }}
                }}
            }}
        }}
    }}
    """
# MAIN
def get_user_prs_and_commits_within_range(github_user: str, past_days: int):
    git_user = GitUser(github_user)
    end_date, start_date = get_target_date(git_user.timezone, past_days, True)
    graphql_query = get_pulls_query(git_user.name, start_date, end_date)
    response = graphql_fetch(gql_github, graphql_query, req_headers)
    if response is None:
        raise Exception("Error fetching pull requests")

    pulls = response["data"]["search"]["edges"]
    valid_data = [
        {
            "title":  pull['node']['title'],
            "commits": filter_commits(pull['node']['commits']['edges'], datetime.strptime(start_date, '%Y-%m-%dT%H:%M:%SZ'), datetime.strptime(end_date, '%Y-%m-%dT%H:%M:%SZ')),
            "key": pull['node']['title'].split()[0]
        } for pull in pulls
    ]
    return [data for data in valid_data if len(data['commits']) > 0]

def filter_commits(commits, start_date, end_date):
    valid_commits = []
    for commit in commits:
        commit_obj = commit['node']['commit']
        commit_date = datetime.strptime(commit_obj['authoredDate'], '%Y-%m-%dT%H:%M:%SZ')
        if start_date <= commit_date <= end_date:
            valid_commits.append(commit_obj['message'])

    return valid_commits

def get_empty_pr_info(key, title):
    return {
        'title': title,
        'key': key,
        'commits': [],
    }

