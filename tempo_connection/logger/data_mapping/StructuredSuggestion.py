from utils.utils import extract_date_and_time, calculate_time_add


class StructuredSuggestionClass:

    def __init__(self):
        self.end_time = None
        self.isJiraStatusChange = None
        self.start_time = None
        self.start_date = None
        self.time_spent = None
        self.jira_issue_id = None
        self.fromStatus = None
        self.toStatus = None
        self.workType = None

    def map_from_data(self, raw_json: dict):
        try:
            self.jira_issue_id = raw_json['task']['originId']
            self.time_spent = raw_json['durationInSeconds']
            date, time = extract_date_and_time(raw_json['started'])

            self.start_date = date
            self.start_time = time

            self.isJiraStatusChange = raw_json['checkpoints'][0]['sourceSystem'] == 'jira' and \
                                      raw_json['checkpoints'][0]['sourceTrigger'] == 'task_status'
            self.fromStatus = None
            self.toStatus = None
            self.end_time = calculate_time_add(self.start_time, self.time_spent)
        except KeyError as e:
            raise ValueError(f"Missing required field: {e}")

    def map_from_attributes(self, attributes: dict):
        try:
            self.jira_issue_id = attributes['issueId']
            self.time_spent = attributes['time_spent']

            self.start_date = attributes['start_date']
            self.start_time = attributes['start_time']

            if attributes['work_type']:
                self.workType = attributes['work_type']

            self.isJiraStatusChange = False
            self.end_time = calculate_time_add(self.start_time, self.time_spent)
        except KeyError as e:
            raise ValueError(f"Missing required field: {e}")


    def set_work_type(self, work_type):
        self.workType = work_type

    def set_from_status(self, from_status):
        self.fromStatus = from_status

    def set_to_status(self, to_status):
        self.toStatus = to_status

    def is_status_change(self):
        return self.isJiraStatusChange

    def add_time_spent(self, seconds_to_add: int):
        self.time_spent += seconds_to_add
        self.end_time = calculate_time_add(self.start_time, self.time_spent)

    def move_time(self, new_start_time: str):
        self.start_time = new_start_time
        self.end_time = calculate_time_add(self.start_time, self.time_spent)

    def __str__(self):
        return (f"Jira Issue ID: {self.jira_issue_id}\nTime Spent: {self.time_spent}\nStart Date: {self.start_date}"
                f"\nStart Time: {self.start_time}\nWork Type: {self.workType}"
                f"\nisJiraStatusChange: {self.isJiraStatusChange}\nFrom Status: {self.fromStatus}"
                f"\nTo Status: {self.toStatus}\nEnd Time: {self.end_time}")
