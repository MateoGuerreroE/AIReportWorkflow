import requests

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