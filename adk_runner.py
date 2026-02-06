import asyncio

from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.genai import types

from adkagents.agent import root_agent  # your ADK email agent

APP_NAME = "agents"

async def run_adk_agent(user_id: str, query_text: str) -> str:
    session_service = InMemorySessionService()
    await session_service.create_session(
        app_name=APP_NAME,
        user_id=user_id,
        session_id=user_id
    )

    runner = Runner(
        agent=root_agent,
        app_name=APP_NAME,
        session_service=session_service
    )

    content = types.Content(
        role="user",
        parts=[types.Part(text=query_text)]
    )

    events = runner.run_async(
        user_id=user_id,
        session_id=user_id,
        new_message=content,
    )

    final_text = "No response generated."
    async for evt in events:
        if evt.is_final_response():
            final_text = evt.content.parts[0].text

    return final_text

# def run_sync(user_id: str, query_text: str) -> str:
#     return asyncio.run(run_adk_agent(user_id, query_text))
