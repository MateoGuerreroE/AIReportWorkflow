from StructuredSuggestion import StructuredSuggestion
from TicketStatusChange import TicketStatusChange
from jira_connection.jira_client import get_jira_status_changes
from utils.utils import extract_date_and_time, is_hour_within_range


def map_raw_suggestions(suggestions: list[dict]) -> tuple[list[StructuredSuggestion], list[TicketStatusChange]]:
    suggestions_result = []
    ticket_status_change_result = []
    for suggestion in suggestions:
        structured_suggestion = StructuredSuggestion(suggestion)
        if structured_suggestion.is_status_change():
            ticket_status_change_result.append(TicketStatusChange(structured_suggestion))
        else:
            suggestions_result.append(structured_suggestion)
    return suggestions_result, ticket_status_change_result

def map_ticket_status_changes_data(ticket_info: TicketStatusChange) -> None:
    ticket_status_changes = get_jira_status_changes(ticket_info.ticket_id, 'mateo.guerrero@omedym.io')
    if len(ticket_status_changes) > 0:
        for status_change_entry in ticket_status_changes:
            date, time = extract_date_and_time(status_change_entry.created)
            if is_hour_within_range(ticket_info.time, time, 15):
                ticket_info.set_from_status(status_change_entry.items[0].fromString)
                ticket_info.set_to_status(status_change_entry.items[0].toString)
                break


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
    suggestions, ticket_status_changes = map_raw_suggestions(test_data)
    return suggestions


test = test_process()
for item in test:
    # map_ticket_status_changes_data(item)
    print(item)
    print("------")
