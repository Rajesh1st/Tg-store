from pyrogram import filters
from database import files, batches, users
from config import *
import uuid

batch_cache = {}

def register_handlers(app):

    async def force_join(client, message):
        try:
            await client.get_chat_member(FORCE_CHANNEL, message.from_user.id)
            return True
        except:
            await message.reply(f"❌ Join {FORCE_CHANNEL} first")
            return False

    @app.on_message(filters.command("start"))
    async def start(client, message):
        if len(message.command) > 1:
            key = message.command[1]
            f = files.find_one({"key": key})
            if f:
                await client.send_cached_media(message.chat.id, f["file_id"])
                return

            b = batches.find_one({"key": key})
            if b:
                for fid in b["files"]:
                    await client.send_cached_media(message.chat.id, fid)
                return

            await message.reply("❌ Invalid link")

    @app.on_message(filters.command("getlink") & filters.reply)
    async def getlink(client, message):
        if not await force_join(client, message): return

        m = message.reply_to_message
        media = m.video or m.document or m.photo or m.sticker
        if not media:
            return await message.reply("❌ Unsupported file")

        key = str(uuid.uuid4())[:12]
        files.insert_one({"key": key, "file_id": media.file_id})

        bot = (await client.get_me()).username
        await message.reply(f"🔗 https://t.me/{bot}?start={key}")

    @app.on_message(filters.command("batch"))
    async def batch(client, message):
        batch_cache[message.from_user.id] = []
        await message.reply("➡️ Forward FIRST file")

    @app.on_message(filters.forwarded)
    async def collect(client, message):
        uid = message.from_user.id
        if uid in batch_cache:
            m = message.video or message.document or message.photo or message.sticker
            if m:
                batch_cache[uid].append(m.file_id)

    @app.on_message(filters.command("done"))
    async def done(client, message):
        uid = message.from_user.id
        data = batch_cache.pop(uid, None)
        if not data:
            return

        key = "BATCH_" + str(uuid.uuid4())[:10]
        batches.insert_one({"key": key, "files": data})

        bot = (await client.get_me()).username
        await message.reply(f"🔗 https://t.me/{bot}?start={key}")

    @app.on_message(filters.command("broadcast") & filters.user(ADMINS))
    async def broadcast(client, message):
        text = message.text.split(None, 1)[1]
        for u in users.find():
            try:
                await client.send_message(u["id"], text)
            except:
                pass
