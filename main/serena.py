
from main import pbot
from main.database import *
from pyrogram import filters, types, enums, errors
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

import config
import random
import re
import requests
import os

developers = [5696053228, 1666544436]


@pbot.on_message(filters.command("start"))
async def start_command(client, message):
    text = (
        f"Hello {message.from_user.mention}! ✨\n"
        "I am **Serena**, advanced AI assistant.\n"
        "I'm here to help make things a little easier.\n\n"
        "**Commands:**\n"
        "• `/chatbot on/off` - Enable/Disable me in groups."
    )
    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("Updates Channel 📢", url="https://t.me/nandhabots")],
        [InlineKeyboardButton("Add Me To Your Group ➕", url=f"https://t.me/{client.me.username}?startgroup=true")]
    ])

    await message.reply_text(text=text, reply_markup=buttons)

async def serena_react(client, message):
     try:
        await pbot.send_reaction(
            chat_id=message.chat.id,
            message_id=message.id,
            emoji=random.choice(['🥰', '❤️', '😁', '🗿', '🤗', '🎉', '😎'])
        )
     except Exception:
          pass

async def ask_serena(message):
    messages = [
        {"role": "system", "content": config.AI_SYS_TXT},
        {"role": "user", "content": message.text}
    ]

    headers = {"Authorization": f"Bearer {config.groq_api_key}"}
    data = {
        "model": "llama-3.1-8b-instant",
        "messages": messages
    }

    try:
        res = requests.post("https://api.groq.com/openai/v1/chat/completions", 
                            headers=headers, json=data)

        if res.status_code == 200:
            answer = res.json()["choices"][0]["message"]["content"]
            return {'reply': answer}
        else:
            return {'reply': '⚠️ Error connecting to AI.'}
    except Exception as e:
         return {'reply': f"❌ {e}"}



     
def admin_only(func):
     async def wrapped(client, message):
         user_id = message.from_user.id
         chat_id = message.chat.id
         if message.chat.type in (enums.ChatType.PRIVATE, enums.ChatType.BOT):
               return await func(client, message)
         else:
            try:
              user = await client.get_chat_member(chat_id, user_id)
            except errors.ChatAdminRequired:
                 return await message.reply_text("**Hello, Make me Admin to activate & deactivate assistant 🥰**")
            
            if user.privileges or user_id == config.serena_id or user_id in developers:
                 return await func(client, message)
     return wrapped





@pbot.on_message(
    (filters.text | filters.caption | filters.sticker | filters.animation) & ~filters.bot,
    group=2
)
async def serena_reply(client, message):
    chat_id = message.chat.id
    chat_type = message.chat.type
    chat_name = message.chat.title or getattr(message.chat, "first_name", "Unknown")
    reply_to = message.reply_to_message

    # Ignore bot's own messages
    if message.from_user and message.from_user.id == config.serena_id:
        return

    # Check if Serena is enabled in chat
    if not get_chat_mode(chat_id, chat_name):
        return

    # =========================
    # 🎯 Handle Media (Sticker/GIF)
    # =========================
    if message.sticker or message.animation:
        if message.sticker:
            try:
                add_chat_sticker(chat_id=chat_id, sticker_id=message.sticker.file_id)
            except Exception as e:
                print(f"Sticker save error: {e}")

        try:
            stickers = get_all_stickers()
            if stickers:
                return await message.reply_sticker(random.choice(stickers))
        except Exception as e:
            print(f"Sticker reply error: {e}")
        return

    # =========================
    # 🧠 Text Processing
    # =========================
    # 1. Basic Setup
    reply_to = message.reply_to_message
    chat_id = message.chat.id
    chat_type = message.chat.type
    
    # Get text from message or caption
    text = (message.text or message.caption or "").strip()
    text_lower = text.lower()
    
    # Define bot details (Ensure these are in your config)
    bot_username = "@serenaaichatbot" 
    bot_name = "serena"

    # 2. 🔹 Detection Logic
    
    # Check if name is mentioned in plain text
    is_name_mention = bot_name in text_lower
    
    # Check if @username is in plain text
    is_username_mention = bot_username in text_lower

    # 3. 🔹 Entity Detection (The most reliable for Telegram)
    # We must check both .entities AND .caption_entities
    is_entity_mention = False
    msg_entities = message.entities or message.caption_entities
    
    if msg_entities:
        for entity in msg_entities:
            if entity.type == enums.MessageEntityType.MENTION:
                # Extract the actual mention string based on offset
                mention_text = text[entity.offset : entity.offset + entity.length].lower()
                if mention_text == bot_username:
                    is_entity_mention = True
                    break

    # 4. 🔹 Reply to bot Detection
    # Ensure IDs are compared as integers to avoid type mismatch
    is_reply_to_bot = False
    if reply_to and reply_to.from_user:
        if int(reply_to.from_user.id) == int(config.serena_id):
            is_reply_to_bot = True

    # 5. 🚀 Decision Logic
    should_reply = (
        chat_type == enums.ChatType.PRIVATE
        or is_username_mention
        or is_entity_mention
        or is_name_mention
        or is_reply_to_bot
    )

    # Logging for debugging
    print(
        f"[SERENA] chat={chat_id} | name_match={is_name_mention} | "
        f"user_match={is_username_mention} | entity_match={is_entity_mention} | "
        f"is_reply={is_reply_to_bot} | DECISION={should_reply}"
    )

    if not should_reply:
        return False
    
    return True



@pbot.on_message(filters.command('chatbot', prefixes=['.', '?', '/']))
@admin_only
async def serena_mode(client, message):
      chat_id = message.chat.id
      modes = {'on': True, 'off': False}
      
      args = message.text.split()
      if len(args) == 2 and args[1].lower() in modes:
           key = args[1].lower()
           mode_val = modes[key]
           chatname = message.chat.title or (message.chat.first_name + ' Chat')
           
           set_chat_mode(chat_id=chat_id, chatname=chatname, mode=mode_val)
           return await message.reply(f'**Serena AI {key.upper()} in {chatname}.**')
      else:
         return await message.reply('Usage: `/chatbot on|off`')
