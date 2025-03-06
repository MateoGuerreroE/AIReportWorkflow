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

def post(url, headers=None, auth=None, body=None):
    if headers is None:
        headers = {}
    try:
        base_response = requests.post(url, headers=headers, auth=auth, json=body)
        try:
            response_json = base_response.json()
            return response_json
        except ValueError:
            print("Response Text:", base_response.text)
            return base_response.text
    except requests.exceptions.RequestException as e:
        print("Request Exception:", e)
        return None

def check_date(date: str, time_delta: int, clean=False) -> bool:
    if not clean:
        clean_date, _ = extract_date_and_time(date)
    else:
        clean_date = date
    target_day = datetime.now() - timedelta(days=time_delta)
    formatted_date = target_day.strftime('%Y-%m-%d')
    return clean_date == formatted_date


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

def is_hour_earlier_than(start_time: str, target_time: str) -> bool:
    base_time = datetime.strptime(start_time, '%H:%M:%S')
    check_time = datetime.strptime(target_time, '%H:%M:%S')

    return base_time <= check_time

def calculate_time_add(time: str, seconds: int) -> str:
    base_time = datetime.strptime(time, '%H:%M:%S')
    new_time = base_time  + timedelta(seconds=seconds)
    return new_time.strftime('%H:%M:%S')