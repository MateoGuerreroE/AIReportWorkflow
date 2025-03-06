from tempo_connection.logger.data_mapping.StructuredSuggestion import StructuredSuggestionClass
from tempo_connection.logger.data_mapping.TempoEntry import TempoEntryClass
from utils import calculate_time_add
from datetime import datetime


def get_tempo_entries(suggestions: list[StructuredSuggestionClass]) -> list[TempoEntryClass]:
    tempo_entries = []
    # This works as long as 11399 is the smallest ticket number (likely always)
    suggestions.sort(key=lambda x: x.jira_issue_id)
    for suggestion in suggestions:
        if suggestion.is_status_change():
            continue
        entry = TempoEntryClass()
        if tempo_entries:
            last_entry = tempo_entries[-1]
            if is_overlapping_or_before(last_entry, suggestion):
                suggestion.move_time(calculate_time_add(last_entry.startTime, last_entry.timeSpentSeconds))
        else: # In case of first entry
            initial_suggestion = next(e for e in suggestions if e.jira_issue_id == '11399')
            entry.map_from_suggestion(initial_suggestion, "")
            tempo_entries.append(entry)
            continue
        entry.map_from_suggestion(suggestion, "")
        tempo_entries.append(entry)
    return tempo_entries


def is_overlapping_or_before(entry: TempoEntryClass, suggestion: StructuredSuggestionClass) -> bool:
    fmt = '%H:%M:%S'

    entry_end_time = datetime.strptime(calculate_time_add(entry.startTime, entry.timeSpentSeconds), fmt)
    entry_start_time = datetime.strptime(entry.startTime, fmt)
    suggestion_start_time = datetime.strptime(suggestion.start_time, fmt)

    return not entry_start_time <= suggestion_start_time <= entry_end_time


def has_issue_id(entry: TempoEntryClass, issue_id: str) -> bool:
    return entry.issueId == issue_id
