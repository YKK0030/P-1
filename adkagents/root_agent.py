# from google.adk.agents import LlmAgent
# from adkagents.email_agent import email_agent
# from adkagents.image_agent import image_agent

# def route_to_email(query: str) -> str:
#     return email_agent.run(query)

# def route_to_image(query: str) -> str:
#     return image_agent.run(query)

# root_agent = LlmAgent(
#     name="root_router",
#     model="gemini-2.5-flash",
#     instruction="""
#         You are a router agent.

#         Decide which specialist agent should handle the request.

#         Rules:
#         - Email-related → email agent
#         - Image generation → image agent
#         - Mixed tasks → call multiple agents and combine results
#         - Casual chat → answer directly
#         """,
#     tools=[route_to_email, route_to_image],
# )

# adkagents/nova_agent.py
from google.adk.agents import LlmAgent
from tools.email_tool import fetch_todays_emails
from tools.image_tool import generate_image
# from tools.task_ool import create_task

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


nova_agent = LlmAgent(
    name="nova",
    model="gemini-2.5-flash",
    instruction="""
You are Nova, a personal AI assistant.

Capabilities:
- Chat naturally
- Summarize and analyze emails
- Generate images from descriptions
- Manage tasks

Rules:
- Use tools whenever real-world data or actions are required.
- Do not hallucinate results from tools.
- Be concise, clear, and friendly.
- If multiple tools are needed, call them in sequence.
""",
    tools=[
        fetch_emails,
        generate_image,
        # create_task,
    ],
)
