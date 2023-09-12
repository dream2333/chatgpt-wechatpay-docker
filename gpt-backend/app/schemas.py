from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel
from tortoise import Tortoise
from app.models import User, Context, SystemPrompt
from tortoise.contrib.pydantic import pydantic_model_creator

Tortoise.init_models(["app.models"], "models")


class Message(BaseModel):
    content: str
    sessionid: UUID


# class PromptListPydantic(BaseModel):
#     id: int
#     name: str
#     description: str

UserPydantic = pydantic_model_creator(User, name="User", exclude=["contexts"])
# ContextGetPydantic = pydantic_model_creator(
#     Context, name="ContextGet", exclude=["user"]
# )
ContextListPydantic = pydantic_model_creator(
    Context, name="ContextList", include=["session_id", "summary", "create_time"]
)
PromptCreatePydantic = pydantic_model_creator(
    SystemPrompt, name="PromptCreate", exclude_readonly=True
)
PromptListPydantic = pydantic_model_creator(
    SystemPrompt, name="PromptList", include=["id", "name", "description"]
)


class ContextGetPydantic(BaseModel):
    session_id: UUID
    content: List[dict]
    prompt: Optional[PromptListPydantic]

    class Config:
        orm_mode = True
