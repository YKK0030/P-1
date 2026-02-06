from google.adk.agents import LlmAgent
from tools.image_tool import generate_image

image_agent = LlmAgent(
    name="image_agent",
    model="gemini-2.5-flash",
    instruction="""
        You generate images from user descriptions.
        Improve prompts before image generation.
        """,
    tools=[generate_image],
)
