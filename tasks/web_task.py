from crewai import Task
from config.config import Config


def create_web_task(agent, user_text: str, history: str = "") -> Task:
    """
    Creates a single web-research task for the agent.
    """

    description = f"""
{Config.SYSTEM_PROMPT}

Conversation history:
{history}

User question:
{user_text}

Instructions:
- Use web search only if needed
- Be concise and accurate
- Do not mention tools or sources unless asked
"""

    return Task(
        description=description.strip(),
        agent=agent,
        expected_output="A clear, helpful answer based on accurate information"
    )
