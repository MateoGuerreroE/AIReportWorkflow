from datetime import datetime
import os
import math

from jira_connection import get_issue_status
from tempo_connection.logger.data_mapping.StructuredSuggestion import StructuredSuggestionClass
from jira_connection.jira_client import get_jira_status_changes
from tempo_connection.logger.data_mapping.tempo_entry_map import get_tempo_entries
from tempo_connection.logger.publish_entries import publish_entries
from utils.utils import extract_date_and_time, is_hour_within_range, is_hour_earlier_than, check_date
from dotenv import load_dotenv

load_dotenv()
WORK_EMAIL = os.getenv("JIRA_EMAIL")
banned_ids = [11399, 16083, 14167]

def filter_raw_data(raw_data: list[dict], is_week=False) -> list[dict]:
    target_data = [val for val in raw_data if val["task"]["originId"] not in banned_ids]
    result = []
    if is_week:  # Tempo Suggestion Capture takes all week data by default
        result = target_data
    else:
        week_day = datetime.now().weekday()
        for entry in raw_data:
            if check_date(entry["started"], 3 if week_day == 0 else 1): # Only those from yesterday
                result.append(entry)
    return result

def get_suggestions(data: list[dict], is_week: bool) -> list[StructuredSuggestionClass]:
    filtered_data = filter_raw_data(data, is_week)
    base_suggestions = map_raw_suggestions(filtered_data)
    if len(base_suggestions):
        base_suggestions.insert(0, get_dsu_suggestion(base_suggestions[0].start_date, False))
    result = get_only_suggestions(base_suggestions)
    return result

def map_raw_suggestions(suggestions: list[dict]) -> list[StructuredSuggestionClass]:
    suggestions_result = []
    for suggestion in suggestions:
        structured_suggestion = StructuredSuggestionClass()
        structured_suggestion.map_from_data(suggestion)
        if structured_suggestion.is_status_change():
            map_status_change_data(structured_suggestion)
            suggestions_result.append(structured_suggestion)
        else:
            suggestions_result.append(structured_suggestion)
    set_work_type(suggestions_result)
    return merge_suggestions_by_time(suggestions_result)

def map_status_change_data(ticket_info: StructuredSuggestionClass) -> None:
    ticket_status_changes = get_jira_status_changes(ticket_info.jira_issue_id, WORK_EMAIL)
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
            return "Designing"
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
            # If there's no change yet of the status, retrieve current status.
            if ticket_change is None:
                suggestion.fromStatus = get_issue_status(suggestion.jira_issue_id, WORK_EMAIL)
            else:
                suggestion.fromStatus = ticket_change.fromStatus
            suggestion.workType = get_ticket_change_work_type(suggestion)

def merge_suggestions_by_time(suggestions: list[StructuredSuggestionClass]) -> list[StructuredSuggestionClass]:
    if len(suggestions) == 0:
        return []

    suggestions.sort(key=lambda suggestion: suggestion.start_time)
    merged_suggestions = [suggestions[0]]

    for i in range (1, len(suggestions)):
        last_suggestion = merged_suggestions[-1]
        current_suggestion = suggestions[i]

        if (last_suggestion.end_time == current_suggestion.start_time
                and last_suggestion.jira_issue_id == current_suggestion.jira_issue_id):
            last_suggestion.add_time_spent(current_suggestion.time_spent)
        elif last_suggestion.jira_issue_id == current_suggestion.jira_issue_id:
            last_suggestion.add_time_spent(current_suggestion.time_spent)
        else:
            merged_suggestions.append(current_suggestion)

    return merged_suggestions

def get_dsu_suggestion(date: str, is_edt: bool) -> StructuredSuggestionClass:
    suggestion = StructuredSuggestionClass()
    if is_edt:
        start_time = '08:30:00'
    else:
        start_time = '09:30:00'
    suggestion.map_from_attributes({
        'issueId': '11399',
        'time_spent': 1800,
        'start_date': date,
        'start_time': start_time,
        'work_type': "Collaborating"
    })
    return suggestion

def complies_with_objective(suggestions: list[StructuredSuggestionClass]) -> bool:
    objective = 28800
    total_time = sum([suggestion.time_spent for suggestion in suggestions])
    return objective <= total_time

def complies_with_threshold(suggestions: list[StructuredSuggestionClass]) -> bool:
    threshold = 18000
    total_time = sum([suggestion.time_spent for suggestion in suggestions])
    return threshold <= total_time

def create_work_batch(suggestions: list[StructuredSuggestionClass]) -> list[StructuredSuggestionClass]:
    if not complies_with_threshold(suggestions):
        raise Exception("Not enough hours logged to create a work batch")

    iterations_left = len(suggestions)
    suggestions.sort(key=lambda suggestion: suggestion.time_spent, reverse=True)
    while not complies_with_objective(suggestions) or suggestions == 0:
        if not suggestions[iterations_left - 1].jira_issue_id == '11399':
            increase_time(suggestions[iterations_left - 1])
        iterations_left -= 1
    suggestions.sort(key=lambda suggestion: suggestion.start_time)
    return suggestions


def increase_time(suggestion: StructuredSuggestionClass) -> None:
    time_increase = math.ceil((suggestion.time_spent * 0.6) / 900) * 900
    suggestion.add_time_spent(time_increase)

def get_only_suggestions(suggestions: list[StructuredSuggestionClass]) -> list[StructuredSuggestionClass]:
    return [suggestion for suggestion in suggestions if not suggestion.is_status_change()]

def process_data(data: list[dict]):
    suggestions = get_suggestions(data, False)
    try:
        step2 = create_work_batch(suggestions)
        return get_tempo_entries(step2)
    except Exception as e:
        print("Threshold not met. Hours will be logged with no modification: ", e)
        return get_tempo_entries(suggestions)
