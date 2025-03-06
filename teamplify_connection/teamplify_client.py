import os
from datetime import datetime, timedelta
import requests
from dotenv import load_dotenv

load_dotenv()

teamplify_token = os.getenv("TEAMPLIFY_TOKEN")
country_id = 'cry_qAEf9TmumPSSLLsb'
teamplify_url = os.getenv("TEAMPLIFY_URL")
invalid_weekdays = [5, 6]



def get_holiday_match(variables, token):
    headers = {
        'Authorization': 'Bearer ' + token,
        'Content-Type': 'application/json',
    }
    query = """
    query GET_HOLIDAY($date: Date, $country: String) {
        viewer {
            currentOrganization {
                holidays (dateFrom: $date, dateTo: $date, countries: [$country]) {
                    edges {
                        node {
                            date
                            workday
                        }
                    }
                }
            }
        }
    }
    """
    try:
        response = requests.post(teamplify_url, json={'query': query, 'variables': variables}, headers=headers)
        return response.json()
    except requests.exceptions.RequestException as e:
        print(e)
        return None


def get_target_days(received_days: int) -> int:
    target_day = datetime.now() - timedelta(days=received_days)
    formatted_date = target_day.strftime('%Y-%m-%d')
    query_variables = {
        "date": formatted_date,
        "country": country_id,
    }
    holiday_data = get_holiday_match(query_variables, teamplify_token)
    holidays = holiday_data['data']['viewer']['currentOrganization']['holidays']['edges']
    if len(holidays) > 0:
        holiday = holidays[0]['node']['date']
        if holiday == formatted_date:
            return False

    weekday = target_day.weekday()
    if received_days != 1 and weekday in invalid_weekdays:
        return 0
    elif weekday == 6:
        return 3
    return 1

def publish_report(variables, token):
    headers = {
        'Authorization': 'Bearer ' + token,
        'Content-Type': 'application/json',
    }
    mutation = """
    mutation CREATE_REPORT($period: ReportPeriod, $text: String!, $date: Date!) {
        upsertReport (report: {
            period: $period,
            published: true,
            text: $text,
            date: $date,
        }) {
            report {
                id
                period
                published
            }
        }
    }
    """

    try:
        response = requests.post(teamplify_url, json={'query': mutation, 'variables': variables}, headers=headers)
        return response.json()
    except requests.exceptions.RequestException as e:
        print(e)
        return None

def send_teamplify_report(date: str, text: str):
    built_variables = {
        'period': 'DAILY',
        'text': text,
        'date': date,
    }
    result = publish_report(variables=built_variables, token=teamplify_token)
    if result is None:
        print('No report was published')
        return None
    else:
        return result





