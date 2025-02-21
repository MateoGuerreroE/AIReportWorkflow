import requests
from datetime import datetime, timedelta


def fetch(url, headers=None, auth=None):
    if headers is None:
        headers = {}
    try:
        base_response = requests.get(url, headers=headers, auth=auth)
        return base_response.json()
    except requests.exceptions.RequestException as e:
        return None

def graphql_fetch(url: str, query: str, headers=None):
    try:
        result = requests.post(url, json={'query': query}, headers=headers)
        return result.json()
    except requests.exceptions.RequestException as e:
        return None

def get_unique_issue_keys(issue_list):
    issue_keys = []
    for issue in issue_list:
        if issue['key'] not in issue_keys:
            issue_keys.append(issue['key'])
    return issue_keys

def remove_key(obj, key):
    obj.pop(key, None)
    return obj

def extract_date_and_time(date_time: str) -> tuple[str, str]:
    dt = datetime.fromisoformat(date_time)
    return dt.strftime('%Y-%m-%d'), dt.strftime('%H:%M:%S')

def is_hour_within_range(start_time: str, target_time: str, delta: int) -> bool:
    base_time = datetime.strptime(start_time, '%H:%M:%S')
    check_time = datetime.strptime(target_time, '%H:%M:%S')

    upper_limit = base_time + timedelta(minutes=delta)

    return base_time <= check_time <= upper_limit