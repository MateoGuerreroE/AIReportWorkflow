from datetime import datetime, timedelta
from github_connection import get_user_prs_and_commits_within_range
from jira_connection import get_ticket_title
from gemini_connection import generate_report_text
from jira_connection import map_issues_description
from teamplify_connection import send_teamplify_report, is_valid_report_day
from tempo_connection import get_tempo_worklog_list, get_empty_worklog
from utils import remove_key
from dotenv import load_dotenv
import os

os.environ["GRPC_VERBOSITY"] = "ERROR"
os.environ["GLOG_minloglevel"] = "2"
load_dotenv()

days_passed = int(os.getenv("DAYS_PASSED"))

def normalize_data(github_prs, tempo_worklog, jira_email):
    result = []
    for pr in github_prs:
        if pr['key'] != '[DEV]':
            tempo_pair = list(filter(lambda x: x['key'] == pr['key'], tempo_worklog))
            if len(tempo_pair) > 0:
                result.append({
                    'key': pr['key'],
                    'title': pr['title'],
                    'commits': pr['commits'],
                    'work_logs': remove_key({**tempo_pair[0]}, 'key'),
                })
            else:
                empty_log = get_empty_worklog(pr['key'])
                result.append({
                    'key': pr['key'],
                    'title': pr['title'],
                    'commits': pr['commits'],
                    'work_logs': remove_key({**empty_log}, 'key'),
                })
        else:
            target_ticket = pr['title'].split()[2]
            title = get_ticket_title(target_ticket, jira_email)
            existent_entry = next((entry for entry in result if entry['key'] == target_ticket), None)
            if existent_entry:
                for item in result:
                    if item['key'] == target_ticket:
                        item['commits'].extend(pr['commits'])
            else:
                empty_log = get_empty_worklog(target_ticket)
                result.append({
                    'key': target_ticket,
                    'title': title,
                    'commits': pr['commits'],
                    'work_logs': remove_key({**empty_log}, 'key'),
                })
    for log in tempo_worklog:
        existent_register = list(filter(lambda x: x['key'] == log['key'], result))
        if len(existent_register) > 0:
            continue
        else:
            title = get_ticket_title(log['key'], jira_email)
            result.append({
                'key': log['key'],
                'title': title,
                'commits': [],
                'work_logs': remove_key({**log}, 'key'),
            })
    return result

def get_developer_work_objects(github_username: str, jira_email: str, passed_days: int):
    prs_info = get_user_prs_and_commits_within_range(github_username, passed_days)
    tempo_logs = get_tempo_worklog_list(passed_days, jira_email)
    normalized_data = normalize_data(prs_info, tempo_logs, jira_email)
    map_issues_description(normalized_data, jira_email)
    return normalized_data

def get_developer_summary(github_username: str, jira_email: str, passed_days: int):
    dev_work = get_developer_work_objects(github_username, jira_email, passed_days)
    generated_report = generate_report_text(dev_work)
    return generated_report

def publish_developer_report(gh_name: str, jira_email: str, days: int) -> str:
    should_report = is_valid_report_day(days)
    if not should_report:
        return "A report should not be published for this day based on received parameters."
    generated_report = get_developer_summary(gh_name, jira_email, days)
    date = datetime.now() - timedelta(days=days)
    formatted_date = date.strftime("%Y-%m-%d")
    report = send_teamplify_report(formatted_date, generated_report)
    print(report)
    return "Report published"

final_result = publish_developer_report('MateoGuerreroE', 'mateo.guerrero@omedym.io', 0)
print(final_result)


