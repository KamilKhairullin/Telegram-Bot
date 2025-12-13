from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from .database import engine, Base, get_db
from .models import User, Chat, Reputation
from .schemas import ReputationUpdate, ReputationResponse

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
