from supabase import create_client
from config.config import Config
from config.logger import get_logger

logger = get_logger()

# ===== INIT CLIENT =====
supabase = create_client(
    Config.SUPABASE_URL,
    Config.SUPABASE_KEY
)


# ===== SAVE MESSAGE =====
def save_message(user_id, role, text):
    try:
        logger.debug(f"Saving message → {role} | {user_id}")

        supabase.table("chats").insert({
            "user_id": user_id,
            "role": role,
            "message": text
        }).execute()

    except Exception as e:
        logger.error(f"Supabase save failed: {e}")


# ===== GET HISTORY =====
def get_history(user_id, limit=1):
    try:
        logger.debug(f"Fetching history for {user_id}")

        data = (
            supabase.table("chats")
            .select("*")
            .eq("user_id", user_id)
            .order("created_at", desc=True)
            .limit(limit)
            .execute()
        )

        msgs = data.data[::-1]

        history = "\n".join(
            [f"{m['role']}: {m['message']}" for m in msgs]
        )

        return history

    except Exception as e:
        logger.error(f"Supabase fetch failed: {e}")
        return ""
