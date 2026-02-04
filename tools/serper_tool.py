from dotenv import load_dotenv
load_dotenv()

from config.config import Config
from crewai_tools import SerperDevTool

def get_serper_tool():
    if not Config.SERPER_API_KEY:
        raise ValueError("SERPER_API_KEY missing")

    return SerperDevTool(api_key=Config.SERPER_API_KEY)
