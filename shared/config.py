import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Токены ботов
    FOUNDER_TOKEN = os.getenv("FOUNDER_TOKEN")
    HELPER_TOKEN = os.getenv("HELPER_TOKEN")
    
    # PostgreSQL (Render)
    DATABASE_URL = os.getenv("DATABASE_URL")
    
    # Mini-App URL
    WEBAPP_URL = os.getenv("WEBAPP_URL", "https://yourapp.onrender.com")
    
    # Настройки
    MAX_TAG_LENGTH = 32

config = Config()