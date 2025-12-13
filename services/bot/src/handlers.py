from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from src.db_client import DBApiClient

router = Router()
api_client = DBApiClient()

@router.message(F.text.in_({"+", "-", "👍", "👎", "➕", "➖"}))
async def reputation_change_handler(message: Message):
    reply = message.reply_to_message
    if not reply:
        return
    if reply.from_user.is_bot:
        return
    if reply.from_user.id == message.from_user.id:
        return

    is_upvote = message.text in ("+", "👍", "➕")
    amount = 1 if is_upvote else -1
    diff_text = "подняли" if is_upvote else "понизили"
    emoji_result = "✅" if is_upvote else "❌"

    new_score = await api_client.update_reputation(
        target_user=reply.from_user, 
        chat=message.chat, 
        amount=amount
    )

    if new_score is not None:
        target_name = reply.from_user.full_name
        
        if is_upvote:
            text = (
                f"Респект! Вы {diff_text} карму пользователю {target_name}.\n"
                f"Теперь его рейтинг: {new_score} {emoji_result}"
            )
        else:
            text = (
                f"Дизлайк! Вы {diff_text} карму пользователю {target_name}.\n"
                f"Теперь его рейтинг: {new_score} {emoji_result}"
            )
        
        await message.reply(text)
    else:
        await message.reply("Ошибка. Бот обосрался..")


@router.message(Command("rating"))
@router.message(F.text.lower().regexp(r"(шпек|шпэк|шпег|bot|бот)[\s,]*рейтинг"))
async def show_rating_handler(message: Message):
    if message.reply_to_message:
        target = message.reply_to_message.from_user
        data = await api_client.get_user_score(message.chat.id, target.id)
        
        if data:
            await message.reply(f"Рейтинг пользователя {data['full_name']}: {data['score']}")
        else:
            await message.reply(f"У пользователя {target.full_name} пока нет рейтинга.")
        return

    top_users = await api_client.get_top_users(message.chat.id)

    if not top_users:
        await message.reply("Пока нет пользователей с рейтингом.")
        return

    text = "🏆 Топ пользователей по рейтингу:\n\n"
    for idx, user in enumerate(top_users, 1):
        emoji = "🥇" if idx == 1 else "🥈" if idx == 2 else "🥉" if idx == 3 else f"{idx}."
        text += f"{emoji} {user['full_name']}: {user['score']}\n"

    await message.reply(text)

@router.message()
async def catch_all(message: Message):
    print(f"DEBUG: I got message: '{message.text}'")