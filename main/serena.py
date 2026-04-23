
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


START_STICKERS = [
  "CAACAgUAAxkBAAEBrV9nWukpft8gmtrZVMkbO4GKlZy0HQACWxUAAnHv2FZkjr7WjG3OjzYE",
  "CAACAgIAAx0CZEWBuAACY1Vp5HITx1GrYTA6UcS09fEySVjoewACXxcAAjqz6UmnEUA60wg8cDsE",
  "CAACAgUAAxkBAAEBrWJnWulBrVl7pq-QRI1QCaMjd6laLAAC2RYAAojK2Va2m-0pJ2vqLzYE"
]

start_gif = "https://graph.org/file/85e65eeb0c23bfe0ac19d-2f376b6c757f254db2.mp4"


@pbot.on_message(filters.command("start"))
async def start_command(client, message):
    chat_id = message.chat.id
    try:
        await client.send_sticker(
            chat_id=chat_id,
            sticker=random.choice(START_STICKERS)
        )
    except Exception:
        pass

    # 2. Define the Inline Buttons
    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("Add Me To Your Group ➕", url="https://t.me/nandhabots", style=enums.ButtonStyle.PRIMARY)],
        [InlineKeyboardButton("Updates Channel 📢", url=f"https://t.me/{client.me.username}?startgroup=true", style=enums.ButtonStyle.PRIMARY)]
    ])

    text = (
        f"Hello {message.from_user.mention}! ✨\n"
        "I am **Serena**, advanced AI assistant.\n"
        "I'm here to help make things a little easier.\n\n"
        "**Commands:**\n"
        "• `/chatbot on/off` - Enable/Disable me in groups."
    )

    await message.reply_animation(animation=start_gif, caption=text, reply_markup=buttons)
    

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

    # =========================
    # 🚀 Decide to Reply (Mention Logic)
    # =========================
    text = (message.text or message.caption or "").strip()
    text_lower = text.lower()

    is_name_mention = "serena" in text_lower
    is_username_mention = f"@{client.me.username.lower()}" in text_lower
    
    is_entity_mention = False
    if message.entities:
        for entity in message.entities:
            if entity.type == enums.MessageEntityType.MENTION:
                mention = text[entity.offset: entity.offset + entity.length].lower()
                if mention == f"@{client.me.username.lower()}":
                    is_entity_mention = True

    is_reply_to_bot = bool(
        reply_to
        and reply_to.from_user
        and reply_to.from_user.id == config.serena_id
    )

    # Main trigger logic
    is_pm = chat_type == enums.ChatType.PRIVATE
    is_mentioned = is_username_mention or is_entity_mention or is_name_mention or is_reply_to_bot

    # If it's a group and no mention occurred, ignore everything
    if not is_pm and not is_mentioned:
        return

    # Check database ONLY for groups (PM works without enabling)
    if not is_pm:
        if not get_chat_mode(chat_id, chat_name):
            return

    # =========================
    # 🎯 Handle Media (Sticker/GIF)
    # =========================
    # Stickers only send if it's a PM OR if the user mentioned the bot in a group
    if message.sticker or message.animation:
        if message.sticker:
            try:
                add_chat_sticker(chat_id=chat_id, sticker_id=message.sticker.file_id)
            except Exception as e:
                print(f"Sticker save error: {e}")

        try:
            stickers = get_all_stickers()
            if stickers:
                # Use .send_sticker instead of .reply_sticker for PMs as requested
                if is_pm:
                    return await client.send_sticker(chat_id, random.choice(stickers))
                else:
                    return await message.reply_sticker(random.choice(stickers))
        except Exception as e:
            print(f"Sticker reply error: {e}")
        return

    # =========================
    # 🧠 AI Text Processing
    # =========================
    try:
        await client.send_chat_action(chat_id, enums.ChatAction.TYPING)
        await serena_react(client, message)

        ai_reply = await ask_serena(message)
        reply_text = ai_reply.get("reply", "I couldn't generate a reply.")

        # In PM, send as a new message. In groups, reply to the user.
        if is_pm:
            return await client.send_message(chat_id, reply_text)
        else:
            return await message.reply_text(reply_text)

    except Exception as e:
        print(f"Serena reply error: {e}")
        return await message.reply_text("Something went wrong while generating a reply.")




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
