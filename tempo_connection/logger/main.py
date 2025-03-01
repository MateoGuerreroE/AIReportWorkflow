import requests
import os

from playwright.sync_api import sync_playwright
from dotenv import load_dotenv
from data_mapping.map_raw_suggestions import map_raw_suggestions

load_dotenv()
JIRA_PASSWORD = os.getenv("JIRA_PASSWORD")

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

    page.goto("https://omedym.atlassian.net/login")
    page.fill("input[type=email]", "mateo.guerrero@omedym.io")
    page.click("#login-submit")
    page.fill("input[type=password]", JIRA_PASSWORD)
    page.click("#login-submit")
    page.wait_for_load_state('networkidle')

    totp_url = "https://personal-totp.vercel.app/api/generate-code"
    call_payload = {
        "appName":"atlassian"
    }
    response = requests.post(totp_url, json=call_payload)
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
    page.goto("https://omedym.atlassian.net/plugins/servlet/ac/io.tempo.jira/tempo-app#!/my-work/week?type=TIME&date=2025-02-19")
    page.wait_for_timeout(6000)
    data = suggestion_plugin_response.filtered_data
    suggestions = map_raw_suggestions(data)
    for item in suggestions:
        print(item)
        print("------")


    browser.close()


