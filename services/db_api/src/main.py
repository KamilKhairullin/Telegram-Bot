from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from .database import engine, Base, get_db
from .models import User, Chat, Reputation
from .schemas import ReputationUpdate, ReputationResponse, UserScore

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()

app = FastAPI(title="SHPEK DB API", lifespan=lifespan)

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.post("/reputation/vote", response_model=ReputationResponse)
async def vote_user(data: ReputationUpdate, db: AsyncSession = Depends(get_db)):
    """
    Атомарное обновление репутации.
    Автоматически создает Юзера и Чат, если их нет.
    """
    user_res = await db.execute(select(User).where(User.telegram_id == data.user.telegram_id))
    user = user_res.scalar_one_or_none()
    
    if not user:
        user = User(
            telegram_id=data.user.telegram_id,
            username=data.user.username,
            full_name=data.user.full_name
        )
        db.add(user)
    else:
        user.username = data.user.username
        user.full_name = data.user.full_name

    chat_res = await db.execute(select(Chat).where(Chat.telegram_id == data.chat.telegram_id))
    chat = chat_res.scalar_one_or_none()
    
    if not chat:
        chat = Chat(
            telegram_id=data.chat.telegram_id,
            title=data.chat.title
        )
        db.add(chat)
    else:
        chat.title = data.chat.title

    await db.flush() 

    rep_res = await db.execute(
        select(Reputation).where(
            Reputation.user_id == user.telegram_id,
            Reputation.chat_id == chat.telegram_id
        )
    )
    reputation = rep_res.scalar_one_or_none()

    if not reputation:
        reputation = Reputation(
            user_id=user.telegram_id, 
            chat_id=chat.telegram_id, 
            score=0
        )
        db.add(reputation)
    
    reputation.score += data.amount
    
    await db.commit()
    await db.refresh(reputation)

    return ReputationResponse(
        user_id=reputation.user_id,
        chat_id=reputation.chat_id,
        new_score=reputation.score
    )

@app.get("/reputation/{chat_id}/top", response_model=list[UserScore])
async def get_top_users(chat_id: int, limit: int = 10, db: AsyncSession = Depends(get_db)):
    """Топ-10 пользователей чата"""
    query = (
        select(User.full_name, User.username, Reputation.score)
        .join(User, User.telegram_id == Reputation.user_id)
        .where(Reputation.chat_id == chat_id)
        .order_by(desc(Reputation.score))
        .limit(limit)
    )
    result = await db.execute(query)
    return [
        UserScore(full_name=row.full_name, username=row.username, score=row.score) 
        for row in result
    ]

@app.get("/reputation/{chat_id}/{user_id}", response_model=UserScore)
async def get_user_reputation(chat_id: int, user_id: int, db: AsyncSession = Depends(get_db)):
    """Рейтинг конкретного юзера"""
    query = (
        select(User.full_name, User.username, Reputation.score)
        .join(User, User.telegram_id == Reputation.user_id)
        .where(Reputation.chat_id == chat_id, Reputation.user_id == user_id)
    )
    result = await db.execute(query)
    row = result.first()
    
    if not row:
         raise HTTPException(status_code=404, detail="User reputation not found")

    return UserScore(full_name=row.full_name, username=row.username, score=row.score)