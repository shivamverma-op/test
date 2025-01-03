import sys
import os
import logging
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram.handlers import MessageHandler, CallbackQueryHandler
import dotenv

# Environment Variables
API_ID = os.getenv("API_ID")
API_HASH = os.getenv("API_HASH")
TOKEN = os.getenv("TOKEN")
SUPPORT_CHAT = os.getenv("SUPPORT_CHAT", "hgbotsupportgroup")
BOT_OWNER_ID = int(os.getenv("OWNER_ID", "7074356361"))

if not (API_ID and API_HASH and TOKEN):
    sys.exit("API_ID, API_HASH, and TOKEN must be set in environment variables.")

# Configure logging
logging.basicConfig(level=logging.INFO, handlers=[logging.FileHandler('logs.txt'),
                                                    logging.StreamHandler()], format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
LOGGER = logging.getLogger(__name__)



# Pyrogram Client Setup
bot = Client(
    "Bot",  # Name of the session
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=TOKEN,
    plugins=dict(root="BGMI")  # Specify the plugin directory here
)
