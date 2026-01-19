from pyrogram import Client
from config import *
from handlers import register_handlers

app = Client(
    "FileStoreBot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

register_handlers(app)
app.run()
