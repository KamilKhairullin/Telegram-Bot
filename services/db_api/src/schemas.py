from pydantic import BaseModel, ConfigDict

class UserData(BaseModel):
    telegram_id: int
    username: str | None
    full_name: str

class ChatData(BaseModel):
    telegram_id: int
    title: str | None

class ReputationUpdate(BaseModel):
    user: UserData
    chat: ChatData
    amount: int

class ReputationResponse(BaseModel):
    user_id: int
    chat_id: int
    new_score: int
    model_config = ConfigDict(from_attributes=True)
