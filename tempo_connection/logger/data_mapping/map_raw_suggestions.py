from tempo_connection.logger.data_mapping.StructuredSuggestion import StructuredSuggestionClass
from jira_connection.jira_client import get_jira_status_changes
from utils.utils import extract_date_and_time, is_hour_within_range, is_hour_earlier_than


def map_raw_suggestions(suggestions: list[dict]) -> list[StructuredSuggestionClass]:
    suggestions_result = []
    for suggestion in suggestions:
        structured_suggestion = StructuredSuggestionClass(suggestion)
        if structured_suggestion.is_status_change():
            map_ticket_status_changes_data(structured_suggestion)
            suggestions_result.append(structured_suggestion)
        else:
            suggestions_result.append(structured_suggestion)
    set_work_type(suggestions_result)
    return suggestions_result

def map_ticket_status_changes_data(ticket_info: StructuredSuggestionClass) -> None:
    ticket_status_changes = get_jira_status_changes(ticket_info.jira_issue_id, 'mateo.guerrero@omedym.io')
    if len(ticket_status_changes) > 0:
        for status_change_entry in ticket_status_changes:
            date, time = extract_date_and_time(status_change_entry.created)
            if is_hour_within_range(ticket_info.start_time, time, 15):
                ticket_info.set_work_type(get_ticket_change_work_type(ticket_info))
                ticket_info.set_from_status(status_change_entry.items[0].fromString)
                ticket_info.set_to_status(status_change_entry.items[0].toString)
                break

def get_ticket_change_work_type(suggestion: StructuredSuggestionClass) -> str:
    status = suggestion.fromStatus
    match status:
        case "To Do":
            return "Design"
        case "Groom" | "Review":
            return "Planning"
        case "In Progress":
            return "Implementing"
        case "PR Raised":
            return "Testing"
        case _:
            return "Testing"

def set_work_type(suggestion_list: list[StructuredSuggestionClass]) -> None:
    ticket_changes = [suggestion for suggestion in suggestion_list if suggestion.is_status_change()]
    for suggestion in suggestion_list:
        if not suggestion.isJiraStatusChange:
            ticket_change = next((change for change in ticket_changes if is_hour_earlier_than(suggestion.start_time, change.start_time)), None)
            if ticket_change is None:
                suggestion.set_work_type("Undetermined")
                continue
            suggestion.set_work_type(ticket_change.workType)

def test_process():
    test_data = [{'id': '81e912f8-0688-43d0-9b28-5df0374a1a89', 'title': '', 'description': '',
                             'task': {'id': 'bbc513d3-1796-409e-87ee-8c5217a5c8b8', 'originId': '27765',
                                      'originEcosystem': 'jira'}, 'groupId': 'bbc513d3-1796-409e-87ee-8c5217a5c8b8',
                             'modelVersion': 'VANILLA', 'modelRevision': '', 'started': '2025-02-17T15:15:00-05:00',
                             'durationInSeconds': 900, 'score': 156, 'checkpoints': [
        {'sourceSystem': 'vscode', 'sourceTrigger': 'save', 'timestamp': '2025-02-17T20:21:15.575Z'}],
                             'taskId': 'bbc513d3-1796-409e-87ee-8c5217a5c8b8'},
                            {'id': '1640d50c-344b-4e8c-9fa3-454a1633ad5a', 'title': '', 'description': '',
                             'task': {'id': '59dcb7f3-c32a-4310-bf85-0a4a32b32a02', 'originId': '28324',
                                      'originEcosystem': 'jira'}, 'groupId': '59dcb7f3-c32a-4310-bf85-0a4a32b32a02',
                             'modelVersion': 'VANILLA', 'modelRevision': '', 'started': '2025-02-17T15:45:00-05:00',
                             'durationInSeconds': 900, 'score': 356, 'checkpoints': [
                                {'sourceSystem': 'jira', 'sourceTrigger': 'task_status',
                                 'timestamp': '2025-02-17T20:59:44.903Z'},
                                {'sourceSystem': 'jira', 'sourceTrigger': 'task_comment',
                                 'timestamp': '2025-02-17T20:59:37.246Z'}],
                             'taskId': '59dcb7f3-c32a-4310-bf85-0a4a32b32a02'}]
    suggestions = map_raw_suggestions(test_data)
    return suggestions

