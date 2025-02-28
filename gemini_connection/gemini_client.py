import google.generativeai as genai
from dotenv import load_dotenv
import os
import json

load_dotenv()

gemini_key = os.getenv("GEMINI_API_KEY")
base_context = ("You will receive a report of what a developer did during the day in an array of objects. You will receive"
                " what commits were done, the time spent divided on categories on the work_log attribute "
                "(with some work logs having a brief description), and a ticket description & title for each ticket, "
                "with last two items being for context only. Tickets usually take more than one day to complete, "
                "so don't assume the ticket is completed. Also, consider 2288 is a testing environment, "
                "so commits merging into 2288 will be for testing. You need to create a single paragraph summary of what "
                "was done by that developer (talking in passive voice) for each ticket key, focusing primarily on the "
                "commit content, and not providing an extra explanation of why the changes were done, try to have a single"
                " paragraph per ticket with a continuous idea, instead of one phrase per commit. Provide response "
                "with MARKDOWN language, where every ticket key It's a subtitle (just the key like OD-1234, not the whole"
                " title). If you receive no commits, create the summary with the worklog information and the worklog "
                "description, but don't be specific with the time spent. Is It clear?")


def get_gemini_client():
    genai.configure(api_key=gemini_key)
    client = genai.GenerativeModel("gemini-1.5-flash")
    return client


def generate_report_text(request):
    client = get_gemini_client()
    history = [
        {"role": "user", "parts": base_context},
        {"role": "model", "parts": "Sure, go ahead and send me the information!"},
    ]
    chat = client.start_chat(history=history)
    base_response = chat.send_message(json.dumps(request))
    chat = None
    return base_response.text
