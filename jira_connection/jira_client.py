from jira import JIRA
from dotenv import load_dotenv

from tempo_connection.logger.data_mapping.TicketStatusChange import TicketStatusChange
from utils import get_unique_issue_keys
import os

load_dotenv()

jira_api_token = os.getenv("JIRA_API_TOKEN")
jira_domain = os.getenv("JIRA_DOMAIN")

class JiraInstance:
    jira = None
    accountId = None
    def __init__(self, domain, email, token):
        self.email = email
        self.jira = JIRA(server=domain, basic_auth=(email, token))
        self.set_account_id()

    def set_account_id(self):
        try:
            user = self.jira.search_users(query=self.email)[0]
            self.accountId = user.accountId
        except IndexError:
            raise Exception('User email not found in JIRA')


def get_jira_instance(domain, email, token) -> JiraInstance:
    return JiraInstance(domain, email, token)

def get_jira_status_changes(ticket_id, email) -> list[dict]:
    instance = get_jira_instance(jira_domain, email, jira_api_token)
    issue = instance.jira.issue(ticket_id, expand="changelog")
    if issue:
        return issue.changelog.histories
    return []

def get_issue_description(email: str, issue: str):
    instance = get_jira_instance(jira_domain, email, jira_api_token)
    issue = instance.jira.issue(issue)
    if issue:
        return issue.fields.description
    return 'None'

def map_issues_description(issue_list, email):
    unique_keys = get_unique_issue_keys(issue_list)
    descriptions_dict = {}
    for key in unique_keys:
        description = get_issue_description(email, key)
        descriptions_dict[key] = description

    for issue in issue_list:
        issue_key = issue['key']
        issue_description = descriptions_dict[issue_key]
        issue['description'] = issue_description

def get_ticket_title(ticket_key, email):
    instance = get_jira_instance(jira_domain, email, jira_api_token)
    issue = instance.jira.issue(ticket_key)
    if issue:
        return issue.fields.summary
    return 'None'



