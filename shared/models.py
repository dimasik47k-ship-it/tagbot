from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class UserRank:
    chat_id: int
    user_id: int
    rank: str
    tag_type: str = 'dm'
    xp: int = 0
    updated_at: Optional[datetime] = None

@dataclass
class User:
    user_id: int
    username: Optional[str] = None
    full_name: Optional[str] = None
    created_at: Optional[datetime] = None
    last_seen: Optional[datetime] = None

@dataclass
class TagType:
    MS = 'ms'      # Message Style - бот переписывает сообщения
    DM = 'dm'      # Direct Message - тег виден только админам