from datetime import datetime

from utils.utils import extract_date_and_time


class StructuredSuggestion:
    workType = None
    description = None

    def __init__(self, raw_json: dict):
        try:
            self.jira_issue_id = raw_json['task']['originId']
            self.time_spent = raw_json['durationInSeconds']
            date, time = extract_date_and_time(raw_json['started'])

            self.start_date = date
            self.start_time = time

            self.__isJiraStatusChange = raw_json['checkpoints'][0]['sourceSystem'] == 'jira' and \
                                      raw_json['checkpoints'][0]['sourceTrigger'] == 'task_status'
        except KeyError as e:
            raise ValueError(f"Missing required field: {e}")

    def set_work_type(self, work_type):
        self.workType = work_type

    def is_status_change(self):
        return self.__isJiraStatusChange

    def set_description(self, description):
        self.description = description

    def __str__(self):
        return (f"Jira Issue ID: {self.jira_issue_id}\nTime Spent: {self.time_spent}\nStart Date: {self.start_date}"
                f"\nStart Time: {self.start_time}\nWork Type: {self.workType}\nDescription: {self.description}")
