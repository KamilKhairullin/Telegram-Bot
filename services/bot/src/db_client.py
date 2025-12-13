import logging
import aiohttp
from aiogram.types import User, Chat
from src.config import config

class DBApiClient:
    def __init__(self):
        self.base_url = config.DB_API_URL
        self.logger = logging.getLogger("api_client")

    async def update_reputation(self, target_user: User, chat: Chat, amount: int) -> int | None:
        # ... (ТОТ ЖЕ КОД, ЧТО БЫЛ РАНЬШЕ) ...
        # (Оставь метод update_reputation без изменений)
        payload = {
            "user": {"telegram_id": target_user.id, "username": target_user.username, "full_name": target_user.full_name},
            "chat": {"telegram_id": chat.id, "title": chat.title or "Private Chat"},
            "amount": amount
        }
        endpoint = f"{self.base_url}/reputation/vote"
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(endpoint, json=payload) as response:
                    response.raise_for_status()
                    data = await response.json()
                    return data["new_score"]
        except Exception as e:
            self.logger.error(f"Failed to vote: {e}")
            return None

    # === НОВЫЕ МЕТОДЫ ===

    async def get_top_users(self, chat_id: int) -> list[dict]:
        endpoint = f"{self.base_url}/reputation/{chat_id}/top"
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(endpoint) as response:
                    if response.status == 200:
                        return await response.json()
                    return []
        except Exception as e:
            self.logger.error(f"Failed to get top: {e}")
            return []

    async def get_user_score(self, chat_id: int, user_id: int) -> dict | None:
        endpoint = f"{self.base_url}/reputation/{chat_id}/{user_id}"
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(endpoint) as response:
                    if response.status == 200:
                        return await response.json()
                    return None
        except Exception as e:
            self.logger.error(f"Failed to get user score: {e}")
            return None