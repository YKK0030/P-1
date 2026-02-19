import asyncio
import os
from dotenv import load_dotenv

from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.genai import types
from memory.cache import cache_history, get_cache
from config.logger import get_logger

from adkagents.root_agent import nova_agent

load_dotenv()

logger = get_logger()
APP_NAME = "agents"


async def run_adk_agent(user_id: str, query_text: str) -> str:
    """
    Run the ADK agent with Redis caching for conversation history.
    Includes past conversation context from Redis.
    """
    
    # STEP 1: Retrieve conversation history from Redis
    conversation_history = get_cache(user_id, limit=20)
    logger.info(f"📚 Retrieved {len(conversation_history.split(chr(10)))} messages from cache")
    
    # STEP 2: Build context-aware query with history
    if conversation_history:
        # Prepend conversation history to give agent context
        full_context = f"""
PREVIOUS CONVERSATION HISTORY:
{conversation_history}

---

CURRENT USER MESSAGE:
{query_text}
"""
        context_query = full_context
    else:
        # First message, no history
        context_query = query_text
    
    logger.debug(f"Full context prepared for user {user_id}")
    
    # STEP 3: Create session service
    session_service = InMemorySessionService()
    await session_service.create_session(
        app_name=APP_NAME,
        user_id=user_id,
        session_id=user_id
    )

    # STEP 4: Create runner with agent
    runner = Runner(
        agent=nova_agent,
        app_name=APP_NAME,
        session_service=session_service
    )

    # STEP 5: Prepare content with context-aware query
    content = types.Content(
        role="user",
        parts=[types.Part(text=context_query)]
    )

    # STEP 6: Run the agent with context
    events = runner.run_async(
        user_id=user_id,
        session_id=user_id,
        new_message=content,
    )

    # STEP 7: Collect the response
    final_text = "No response generated."
    async for evt in events:
        if evt.is_final_response():
            final_text = evt.content.parts[0].text

    # STEP 8: Cache both user message and assistant response
    cache_history(user_id, f"user: {query_text}")
    cache_history(user_id, f"assistant: {final_text}")
    logger.info(f"✅ Conversation cached for {user_id}")

    return final_text
