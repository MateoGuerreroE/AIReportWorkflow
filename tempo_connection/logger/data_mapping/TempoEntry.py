from dotenv import load_dotenv
import os

from tempo_connection.logger.data_mapping.StructuredSuggestion import StructuredSuggestionClass

load_dotenv()

class TempoEntryClass:
    attributes = None
    description = ''
    issueId = ''
    startDate = ''
    startTime = ''
    timeSpentSeconds = 0

    def __init__(self):
        self.authorAccountId = os.getenv("TEMPO_AUTHOR_ID")
        self.is_logged = False

    def map_from_suggestion(self, suggestion: StructuredSuggestionClass, description: str):
        self.description = description
        self.issueId = suggestion.jira_issue_id
        self.startDate = suggestion.start_date
        self.startTime = suggestion.start_time
        self.timeSpentSeconds = suggestion.time_spent
        self.set_work_type(suggestion.workType)

    def set_work_type(self, work_type: str):
        self.attributes = [
            {
                "key": "_WorkType_",
                "value": work_type
            }
        ]

    def __str__(self):
        return (f"Description: {self.description}\nIssue ID: {self.issueId}\nStart Date: {self.startDate}"
                f"\nStart Time: {self.startTime}\nTime Spent: {self.timeSpentSeconds}\nAuthor Account ID: {self.authorAccountId}"
                f"\nAttributes: {self.attributes}")

    def to_dict(self):
        return {
            "description": self.description,
            "startDate": self.startDate,
            "startTime": self.startTime,
            "timeSpentSeconds": self.timeSpentSeconds,
            "authorAccountId": self.authorAccountId,
            "attributes": self.attributes
        }

