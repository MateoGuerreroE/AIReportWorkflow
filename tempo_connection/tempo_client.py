from datetime import datetime, timedelta
from requests.auth import HTTPBasicAuth
from utils import fetch, get_unique_issue_keys
from dotenv import load_dotenv
import os

tempo_url = 'https://api.tempo.io/4/worklogs'
banned_ids = [11399, 16083, 14167] # Ids from time-tracking or env issues, like OA-5

load_dotenv()

jira_api_token = os.getenv("JIRA_API_TOKEN")
tempo_api_token = os.getenv("TEMPO_API_TOKEN")

def get_ranged_work_logs(start_date: str, end_date: str):
    tempo_headers = {'Authorization': 'Bearer ' + tempo_api_token}
    tempo_built_url = f"{tempo_url}?from={start_date}&to={end_date}"

    response = fetch(tempo_built_url, headers=tempo_headers)
    if response is None:
        raise Exception('Unable to fetch tempo entries')
    return response['results']

def get_category_spent_time(category, issue_list):
    total_time = 0
    for issue in issue_list:
        if issue['category'] == category:
            total_time += issue['time_spent']
    return total_time

def write_categories_spent_time(issue_key, issue_list):
    tempo_categories = ['Implementing', 'Testing', 'Investigating', 'Planning', 'Designing', 'Other', 'Collaborating',
                        'Tooling']
    issue_key_list = []
    result_object = {}
    for issue in issue_list:
        if issue['key'] == issue_key:
            issue_key_list.append(issue)
    for selected_issue in issue_key_list:
        result_object['key'] = selected_issue['key']
        for category in tempo_categories:
            result_object[category] = get_category_spent_time(category, issue_key_list)
        if selected_issue['description'] is not None:
            result_object['description'] = selected_issue['description']
    return result_object

def map_issues_keys(issue_list, jira_email):
    consulted_issues = {}
    result = []
    auth = HTTPBasicAuth(jira_email, jira_api_token)
    for issue_info in issue_list:
        if issue_info['issue']['id'] in banned_ids:
            continue
        if issue_info['issue']['id'] not in consulted_issues:
            issue_jira_info = fetch(issue_info['issue']['self'], auth=auth)
            if issue_jira_info is None:
                raise Exception('Unable to fetch issue on JIRA')
            issue_info['issue']['key'] = issue_jira_info['key']
        else:
            key = consulted_issues[issue_info['issue']['id']]
            issue_info['issue']['key'] = key
        result.append({
            'id': issue_info['issue']['id'],
            'key': issue_info['issue']['key'],
            'description': issue_info['description'],
            'time_spent': issue_info['timeSpentSeconds'],
            'category': issue_info['attributes']['values'][0]['value'],
        })
    return result

def get_tempo_worklog_list(days_ago: int, email: str):
    target_day = datetime.now() - timedelta(days=days_ago)
    formatted_date = target_day.strftime('%Y-%m-%d')
    tempo_work_logs = get_ranged_work_logs(formatted_date, formatted_date)
    mapped_logs = map_issues_keys(tempo_work_logs, email)
    unique_keys = get_unique_issue_keys(mapped_logs)
    result = []
    for key in unique_keys:
        result.append(write_categories_spent_time(key, mapped_logs))
    return result

def get_empty_worklog(key):
    return {
        'key': key,
        'Implementing': 0,
        'Testing': 0,
        'Investigating': 0,
        'Planning': 0,
        'Designing': 0,
        'Other': 0,
        'Collaborating': 0,
        'Tooling': 0,
    }

