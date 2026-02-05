import asyncio

from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.genai import types

from adkagents.agent import root_agent  # your ADK email agent

APP_NAME = "email_app"

async def run_adk_agent(user_id: str, query_text: str) -> str:
    # Create a session for this chat/user
    session_service = InMemorySessionService()
    session = await session_service.create_session(
        app_name=APP_NAME,
        user_id=user_id,
        session_id=user_id  # can reuse user_id for simplicity
    )

    # Create Runner that will drive your agent
    runner = Runner(
        agent=root_agent,
        app_name=APP_NAME,
        session_service=session_service
    )

    # Build the event content for the user's message
    content = types.Content(role="user", parts=[types.Part(text=query_text)])

    # Start running the agent
    events = runner.run_async(
        user_id=user_id,
        session_id=user_id,
        new_message=content,
    )

    final_text = ""
    async for evt in events:
        # Only pick up the final response event
        if evt.is_final_response():
            final_text = evt.content.parts[0].text
    return final_text


def run_sync(user_id: str, query_text: str) -> str:
    return asyncio.run(run_adk_agent(user_id, query_text))
