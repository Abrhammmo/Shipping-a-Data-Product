from pydantic import BaseModel
from typing import List

class TopProduct(BaseModel):
    term: str
    frequency: int

class ChannelActivity(BaseModel):
    date: str
    message_count: int

class MessageSearchResult(BaseModel):
    message_id: int
    channel_key: str
    message_text: str
    date: str

class VisualContentStat(BaseModel):
    channel_key: str
    image_count: int
    promotional_count: int
