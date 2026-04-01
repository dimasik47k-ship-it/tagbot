import asyncpg
import logging
from typing import Optional, Dict, List
from shared.config import config

logger = logging.getLogger(__name__)

class Database:
    def __init__(self, dsn: str = None):
        self.dsn = dsn or config.DATABASE_URL
        self.pool = None

    async def connect(self):
        """Подключение к PostgreSQL"""
        try:
            self.pool = await asyncpg.create_pool(self.dsn, min_size=5, max_size=20)
            await self._init_tables()
            logger.info("✅ Database connected")
        except Exception as e:
            logger.error(f"❌ Database connection failed: {e}")
            raise

    async def disconnect(self):
        """Отключение"""
        if self.pool:
            await self.pool.close()
            logger.info("Database disconnected")

    async def _init_tables(self):
        """Создание таблиц"""
        async with self.pool.acquire() as conn:
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS user_ranks (
                    chat_id BIGINT NOT NULL,
                    user_id BIGINT NOT NULL,
                    rank TEXT DEFAULT '',
                    tag_type TEXT DEFAULT 'dm',
                    xp INTEGER DEFAULT 0,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (chat_id, user_id)
                )
            """)
            
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id BIGINT PRIMARY KEY,
                    username TEXT,
                    full_name TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

    async def set_rank(self, chat_id: int, user_id: int, rank: str, tag_type: str = 'dm') -> bool:
        async with self.pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO user_ranks (chat_id, user_id, rank, tag_type, updated_at)
                VALUES ($1, $2, $3, $4, CURRENT_TIMESTAMP)
                ON CONFLICT (chat_id, user_id) 
                DO UPDATE SET rank = $3, tag_type = $4, updated_at = CURRENT_TIMESTAMP
            """, chat_id, user_id, rank, tag_type)
            return True

    async def get_rank(self, chat_id: int, user_id: int) -> Optional[Dict]:
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT rank, tag_type FROM user_ranks WHERE chat_id = $1 AND user_id = $2",
                chat_id, user_id
            )
            return dict(row) if row else None

    async def delete_rank(self, chat_id: int, user_id: int) -> bool:
        async with self.pool.acquire() as conn:
            result = await conn.execute(
                "DELETE FROM user_ranks WHERE chat_id = $1 AND user_id = $2",
                chat_id, user_id
            )
            return result != "DELETE 0"

    async def get_top_ranks(self, chat_id: int, limit: int = 10) -> List[Dict]:
        async with self.pool.acquire() as conn:
            rows = await conn.fetch("""
                SELECT user_id, rank, tag_type, xp 
                FROM user_ranks 
                WHERE chat_id = $1 AND rank != '' 
                ORDER BY xp DESC, updated_at DESC 
                LIMIT $2
            """, chat_id, limit)
            return [dict(row) for row in rows]

    async def save_user(self, user_id: int, username: str, full_name: str):
        async with self.pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO users (user_id, username, full_name, last_seen)
                VALUES ($1, $2, $3, CURRENT_TIMESTAMP)
                ON CONFLICT (user_id) DO UPDATE SET username = $2, full_name = $3, last_seen = CURRENT_TIMESTAMP
            """, user_id, username, full_name)

    async def get_user(self, user_id: int) -> Optional[Dict]:
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT user_id, username, full_name, created_at FROM users WHERE user_id = $1",
                user_id
            )
            return dict(row) if row else None

# Глобальный экземпляр
db = Database()