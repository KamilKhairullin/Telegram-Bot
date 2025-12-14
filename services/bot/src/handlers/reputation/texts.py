from typing import Final

EMOJI_LIKE: Final = "👍"
EMOJI_DISLIKE: Final = "❌"
EMOJI_GOLD: Final = "🥇"
EMOJI_SILVER: Final = "🥈"
EMOJI_BRONZE: Final = "🥉"
EMOJI_TROPHY: Final = "🏆"

ERROR_GENERAL: Final = "Ошибка. Бот обосрался.."
NO_USERS_WITH_RATING: Final = "Пока нет пользователей с рейтингом."
TOP_USERS_HEADER: Final = "🏆 Топ пользователей по рейтингу:\n\n"


def format_reputation_increased(username: str, score: int) -> str:
    return (
        f"Лайк! Вы повысили карму пользователю {username}.\n"
        f"Теперь его рейтинг: {score} {EMOJI_LIKE}"
    )


def format_reputation_decreased(username: str, score: int) -> str:
    return (
        f"Дизлайк! Вы понизили карму пользователю {username}.\n"
        f"Теперь его рейтинг: {score} {EMOJI_DISLIKE}"
    )


def format_user_rating(username: str, score: int) -> str:
    return f"Рейтинг пользователя {username}: {score}"


def format_no_rating(username: str) -> str:
    return f"У пользователя {username} пока нет рейтинга."


def get_position_emoji(position: int) -> str:
    match position:
        case 1:
            return EMOJI_GOLD
        case 2:
            return EMOJI_SILVER
        case 3:
            return EMOJI_BRONZE
        case _:
            return f"{position}."


def format_top_user_line(position: int, username: str, score: int) -> str:
    emoji = get_position_emoji(position)
    return f"{emoji} {username}: {score}\n"
