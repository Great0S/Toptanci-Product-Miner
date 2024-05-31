from logging import config as Config
import logging
import os
from deep_translator import GoogleTranslator
from pydantic import BaseSettings
from config.logger import log_config

# Declaring global variables
class Settings(BaseSettings):
    
    # Logger config
    Config.dictConfig(log_config)
    logger: logging.Logger = logging.getLogger('mainLog')
    logs_dir: str = 'logs/'
    
    # Translation
    turk_translate: GoogleTranslator = GoogleTranslator(source='tr', target='en')
    english_translate: GoogleTranslator = GoogleTranslator(source='en', target='ar')
    arabic_translate: GoogleTranslator = GoogleTranslator(source='ar', target='en')

    # Telegram API Config
    api_id: int = os.getenv('BFAPIID')
    api_hash: str = os.getenv('BFAPIHASH')

    # Telegram BOT info
    username: str = os.getenv('BFUSERNAME')
    phone: int = os.getenv('PHONE')
    token: str = os.getenv('BFBOTTOKEN')
    bot_id: str = os.getenv('BFBOTID')
    session_name: str = 'tele_bot'

    # Telegram Channels info
    women_ids: list = [os.getenv('CHANNEL1'), os.getenv('CHANNEL2'), os.getenv('CHANNEL3'), os.getenv('CHANNEL4'), os.getenv('CHANNEL5')]

    # Ecwid info    
    category_id: int = 127443592

    # Ecwid connection info
    products_url: str = "https://app.ecwid.com/api/v3/63690252/products"
    category_url: str = "https://app.ecwid.com/api/v3/63690252/categories"
    ecwid_token: str =  f"?token={os.getenv('ECWIDTOKEN')}"
    payload: dict = {}
    ecwid_headers: dict = {
    "Authorization": f"Bearer {os.getenv('ECWIDTOKEN')}",
    "Content-Type": 'application/json;charset: utf-8'
    }

    class Config:
        case_sensitive = True

settings = Settings()