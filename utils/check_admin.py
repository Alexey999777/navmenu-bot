# utils/check_admin.py
from database import is_user_channel_admin

async def require_channel_admin(user_id: int, channel_id: int) -> bool:
    return await is_user_channel_admin(user_id, channel_id)
