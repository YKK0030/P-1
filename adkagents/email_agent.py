from google.adk.agents.llm_agent import Agent
import os
import pickle
import imaplib
import email
import datetime
from email.header import decode_header
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from tools.email_tool import fetch_todays_emails
from google.adk.agents.sequential_agent import SequentialAgent
from google.adk.agents.llm_agent import LlmAgent

def fetch_emails() -> dict:
    """
    Fetch today's Gmail messages and return structured data.
    Returns:
        {"status":"success", "emails":[{...},...]} on success
        {"status":"error", "message":"..."} on failure
    """
    try:
        emails = fetch_todays_emails()
        return {"status": "success", "emails": emails}
    except Exception as e:
        return {"status": "error", "message": str(e)}

email_agent = Agent(
    model='gemini-2.5-flash',
    name='email_reader_agent',
    description='Your name is NOVA and YAdnit is the one who made you, Use fetch_emails() tool to get today’s emails, then summarize them into short form. and also tell me todays total number of mails. And tell me the ones with high priotity. like the most important one',
    instruction="""
        You are Nova, a personal AI assistant.

        You can:
        - chat naturally with the user
        - answer questions about yourself
        - summarize emails
        - call tools when needed

        If the user asks about emails, call the email tool.
        If the user is chatting, respond conversationally.
        Be concise, helpful, and friendly.
        """,
    tools=[fetch_emails],
)

# root_agent = SequentialAgent(
#     name="finalresult_agent",
#     sub_agents=[mailreader_agent]
# )
