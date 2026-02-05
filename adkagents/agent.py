from google.adk.agents.llm_agent import Agent
import os
import pickle
import imaplib
import email
import datetime
from email.header import decode_header
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from emailTool import fetch_todays_emails
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


mailreader_agent = Agent(
    model='gemini-2.5-flash',
    name='email_reader_agent',
    description='Fetch today’s Gmail messages and summarize them.',
    instruction='Use fetch_emails() tool to get today’s emails, then summarize them into short form.',
    tools=[fetch_emails],
)

email_summary_agent = Agent(
    name="email_summary_agent",
    model="gemini-2.5-flash",
    instruction="Take email content and produce a concise summary.",
    description="Summarizes email text."
)

finalresult_agent = SequentialAgent(
    name="finalresult_agent",
    model="gemini-2.5-flash",
    agents=[mailreader_agent, email_summary_agent],
    instruction="Fetch today's emails and summarize them concisely.",
    description="Fetches and summarizes today's Gmail messages."
)

root_agent = finalresult_agent