from tempo_connection.logger.data_mapping.StructuredSuggestion import StructuredSuggestion


class TicketStatusChange:
    from_status = None
    to_status = None
    def __init__(self, structured_suggestion: StructuredSuggestion):
        self.ticket_id = structured_suggestion.jira_issue_id
        self.date = structured_suggestion.start_date
        self.time = structured_suggestion.start_time

    def set_from_status(self, from_status):
        self.from_status = from_status

    def set_to_status(self, to_status):
        self.to_status = to_status

    def __str__(self):
        return (f"Ticket ID: {self.ticket_id}\nDate: {self.date}\nTime: {self.time}\nFrom Status: {self.from_status}\nTo Status: {self.to_status}")




