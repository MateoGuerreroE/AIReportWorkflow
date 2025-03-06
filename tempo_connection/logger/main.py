import requests
import os

from playwright.sync_api import sync_playwright
from dotenv import load_dotenv
from data_mapping.map_raw_suggestions import map_raw_suggestions
from tempo_connection.logger.data_mapping.map_raw_suggestions import process_data
from tempo_connection.logger.publish_entries import publish_entries

load_dotenv()
JIRA_PASSWORD = os.getenv("JIRA_PASSWORD")
JIRA_EMAIL = os.getenv("JIRA_EMAIL")
JIRA_DOMAIN = os.getenv("JIRA_DOMAIN")
TOTP_URL = os.getenv("TOTP_URL")

class ResponseFilter:
    def __init__(self):
        self.filtered_data = None

    def filter_response(self, resp):
        if "suggestions/" in resp.url:
            try:
                self.filtered_data = resp.json()
            except:
                print("Could not parse JSON")


with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    context = browser.new_context()

    page = context.new_page()

    page.goto(JIRA_DOMAIN)
    page.fill("input[type=email]", JIRA_EMAIL)
    page.click("#login-submit")
    page.fill("input[type=password]", JIRA_PASSWORD)
    page.click("#login-submit")
    page.wait_for_load_state('networkidle')

    call_payload = {
        "appName":"atlassian"
    }
    response = requests.post(TOTP_URL, json=call_payload)
    if response.status_code == 200:
        api_response = response.json()
        totp_code = api_response.get("data", "")
        page.fill("input[type=tel]", totp_code)
    else:
        print("Failed to get totp code")
        browser.close()

    suggestion_plugin_response = ResponseFilter()
    page.on("response", suggestion_plugin_response.filter_response)
    page.wait_for_timeout(6000)
    page.goto(JIRA_DOMAIN + "/plugins/servlet/ac/io.tempo.jira/tempo-app#!/my-work/week?type=TIME")
    page.wait_for_timeout(6000)
    data = suggestion_plugin_response.filtered_data
    suggestions = process_data(data)
    for item in suggestions:
        print(item)
        print("------")
    publish_entries(suggestions)


    browser.close()


