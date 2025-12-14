from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import Message

from src.clients.db_client import DBApiClient

from . import texts

router = Router()
api_client = DBApiClient()


@router.message(F.text.regexp(r"^\++$"))
async def handle_plus(message: Message) -> None:
    reply = message.reply_to_message
    if not reply:
        return
    if reply.from_user.is_bot:
        return
    if reply.from_user.id == message.from_user.id:
        return

    new_score = await api_client.update_reputation(
        target_user=reply.from_user, chat=message.chat, amount=1
    )

    if new_score == 'COOLDOWN':
        await message.reply(texts.COOLDOWN_MESSAGE)
        return

    if new_score is not None:
        text = texts.format_reputation_increased(
            username=reply.from_user.full_name, score=new_score
        )
        await message.reply(text)
    else:
        await message.reply(texts.ERROR_GENERAL)


@router.message(F.text.regexp(r"^\-+$"))
async def handle_minus(message: Message) -> None:
    reply = message.reply_to_message
    if not reply:
        return
    if reply.from_user.is_bot:
        return
    if reply.from_user.id == message.from_user.id:
        return

    new_score = await api_client.update_reputation(
        target_user=reply.from_user, chat=message.chat, amount=-1
    )

    if new_score == 'COOLDOWN':
        await message.reply(texts.COOLDOWN_MESSAGE)
        return

    if new_score is not None:
        text = texts.format_reputation_decreased(
            username=reply.from_user.full_name, score=new_score
        )
        await message.reply(text)
    else:
        await message.reply(texts.ERROR_GENERAL)


@router.message(Command("rating"))
@router.message(F.text.lower().regexp(r"(шпек|шпэк|шпег|bot|бот)[\s,]*рейтинг"))
async def show_rating_handler(message: Message) -> None:
    if message.reply_to_message:
        await _show_user_rating(message)
    else:
        await _show_leaderboard(message)


async def _show_user_rating(message: Message) -> None:
    target = message.reply_to_message.from_user
    data = await api_client.get_user_score(message.chat.id, target.id)

    if data:
        text = texts.format_user_rating(username=data["full_name"], score=data["score"])
    else:
        text = texts.format_no_rating(username=target.full_name)

    await message.reply(text)


async def _show_leaderboard(message: Message) -> None:
    top_users = await api_client.get_top_users(message.chat.id)

    if not top_users:
        await message.reply(texts.NO_USERS_WITH_RATING)
        return

    lines = [texts.TOP_USERS_HEADER]
    for idx, user in enumerate(top_users, start=1):
        lines.append(
            texts.format_top_user_line(
                position=idx, username=user["full_name"], score=user["score"]
            )
        )

    await message.reply("".join(lines))
