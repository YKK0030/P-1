import os
from dotenv import load_dotenv
from config.logger import get_logger

load_dotenv()
logger = get_logger()


class Config:
    TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY")
    SERPER_API_KEY = os.getenv("SERPER_API_KEY")
    REDIS_URL = os.getenv("REDIS_URL")
    MODEL = os.getenv("MODEL_NAME", "gemini-2.5-flash")
    USER_EMAIL = os.getenv("USER_EMAIL")

    # System prompt
    SYSTEM_PROMPT = """
You are Nova, a personal AI assistant and technical buddy.

Personality:
- Smart, practical, and concise
- Talk like a friendly engineer, not a professor
- Casual tone, not robotic or overly formal
- Slightly witty and motivating when needed
- Supportive but honest
- No fluff or long lectures

Behavior rules:
- Give direct answers first, explanations second
- Prefer actionable steps over theory
- Keep responses short unless detail is requested
- Use bullet points when explaining
- Help with coding, debugging, system design, productivity, and life clarity
- If unsure, say you're unsure instead of guessing
- Never overcomplicate simple problems

Style:
- Talk like a tech-savvy best friend
- Be clear, structured, and practical
- Avoid emojis unless casual
- Avoid long essays

Goal:
Help the user grow, build projects, and stay mentally clear while keeping conversations natural and human.
"""

    # ===== API KEY ROTATION SYSTEM =====
    
    @classmethod
    def get_gemini_api_keys(cls) -> list:
        """
        Get all available Gemini API keys from environment variables.
        Supports: GEMINI_API_KEY, GEMINI_API_KEY_2, GEMINI_API_KEY_3, etc.
        """
        keys = []
        
        # Primary key
        primary = os.getenv("GEMINI_API_KEY")
        if primary:
            keys.append(primary)
        
        # Additional keys
        counter = 2
        while True:
            key = os.getenv(f"GEMINI_API_KEY_{counter}")
            if not key:
                break
            keys.append(key)
            counter += 1
        
        if not keys:
            logger.warning("⚠️ No Gemini API keys found in environment!")
        else:
            logger.info(f"✅ Found {len(keys)} Gemini API key(s)")
        
        return keys

    @classmethod
    def get_image_api_keys(cls) -> list:
        """
        Get all available Image generation API keys.
        Supports: GENAI_API_KEY_IMAGE, GENAI_API_KEY_IMAGE_2, etc.
        """
        keys = []
        
        # Primary key
        primary = os.getenv("GENAI_API_KEY_IMAGE")
        if primary:
            keys.append(primary)
        
        # Additional keys
        counter = 2
        while True:
            key = os.getenv(f"GENAI_API_KEY_IMAGE_{counter}")
            if not key:
                break
            keys.append(key)
            counter += 1
        
        if not keys:
            logger.warning("⚠️ No Image API keys found in environment!")
        else:
            logger.info(f"✅ Found {len(keys)} Image API key(s)")
        
        return keys


class APIKeyRotator:
    """
    Manages API key rotation when tokens are exhausted.
    Tracks which keys have failed and rotates to the next available one.
    """
    
    def __init__(self, api_type: str = "gemini"):
        """
        Initialize the API key rotator.
        
        Args:
            api_type: Type of API ('gemini' or 'image')
        """
        self.api_type = api_type
        self.current_index = 0
        
        if api_type == "gemini":
            self.keys = Config.get_gemini_api_keys()
        elif api_type == "image":
            self.keys = Config.get_image_api_keys()
        else:
            raise ValueError(f"Unknown API type: {api_type}")
        
        if not self.keys:
            raise RuntimeError(f"No {api_type} API keys configured!")
        
        logger.info(f"🔑 APIKeyRotator initialized for '{api_type}' with {len(self.keys)} key(s)")

    def get_current_key(self) -> str:
        """Get the current active API key."""
        return self.keys[self.current_index]

    def rotate_to_next_key(self) -> bool:
        """
        Rotate to the next available API key.
        
        Returns:
            True if rotation successful, False if no more keys available
        """
        if self.current_index >= len(self.keys) - 1:
            logger.error(f"❌ All {self.api_type} API keys exhausted!")
            return False
        
        self.current_index += 1
        key_preview = self.keys[self.current_index][:8] + "..." if len(self.keys[self.current_index]) > 8 else "***"
        logger.warning(f"⚠️ Rotating to {self.api_type} API key #{self.current_index + 1}/{len(self.keys)} ({key_preview})")
        return True

    def reset(self) -> None:
        """Reset to the first API key."""
        self.current_index = 0
        logger.info(f"🔄 Reset {self.api_type} API key rotator to first key")

    def get_status(self) -> dict:
        """Get current rotator status."""
        return {
            "api_type": self.api_type,
            "current_key_index": self.current_index + 1,
            "total_keys": len(self.keys),
            "keys_remaining": len(self.keys) - self.current_index,
            "current_key_preview": self.keys[self.current_index][:8] + "..."
        }
