from tempo_connection.logger.data_mapping.TempoEntry import TempoEntryClass

from dotenv import load_dotenv
import os

from tempo_connection.logger.data_mapping.tempo_entry_map import has_issue_id
from utils import post

load_dotenv()

TEMPO_API = os.getenv("TEMPO_API_TOKEN")

def publish_entry_bulk(issue_id: str, entries: list[TempoEntryClass]) -> None:
    headers = {'Authorization': 'Bearer ' + TEMPO_API}
    tempo_url = f"https://api.us.tempo.io/4/worklogs/issue/{issue_id}/bulk"
    body = [entry.to_dict() for entry in entries]
    response = post(tempo_url, headers=headers, body=body)
    if response is None:
        raise Exception('Unable to publish tempo entries')

def publish_entries(entries: list[TempoEntryClass]) -> None:
    for entry in entries:
        if not entry.is_logged:
            related_entries = get_entries_from_same_issue(entry.issueId, entries)
            publish_entry_bulk(entry.issueId, related_entries)
            print(f"Entries published for issue {entry.issueId}")

def get_entries_from_same_issue(issue_id: str, entries: list[TempoEntryClass]) -> list[TempoEntryClass]:
    valid_entries = []
    for entry in entries:
        if has_issue_id(entry, issue_id):
            entry.is_logged = True
            valid_entries.append(entry)
    return valid_entries