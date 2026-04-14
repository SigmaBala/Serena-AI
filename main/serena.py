
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
    
    # 1. Ignore bot's own messages
    if message.from_user and message.from_user.id == config.serena_id:
        return

    # 2. Logic: Only reply if it's a Private Chat OR if someone is replying to the bot in a group
    is_pm = (chat_type == "private")
    is_reply_to_bot = (
        message.reply_to_message and 
        message.reply_to_message.from_user and 
        message.reply_to_message.from_user.id == config.serena_id
    )

    if not (is_pm or is_reply_to_bot):
        return

    # 3. Check if Serena is enabled in chat
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
                chosen_sticker = random.choice(stickers)
                
                # If it's a Private Chat, send without quoting the user's message
                if is_pm:
                    return await client.send_sticker(chat_id, chosen_sticker)
                
                # If it's a group reply, use standard reply behavior
                return await message.reply_sticker(chosen_sticker)
                
        except Exception as e:
            print(f"Sticker reply error: {e}")
        return

    # =========================
    # 🧠 Text Processing
    # =========================
    text = (message.text or message.caption or "").strip()
    text_lower = text.lower()

    # 🔹 Simple detection (fast & reliable)
    is_name_mention = "serena" in text_lower
    is_username_mention = "@serenaaichatbot" in text_lower

    # 🔹 Telegram entity mention detection (best accuracy)
    is_entity_mention = False
    if message.entities:
        for entity in message.entities:
            if entity.type == "mention":
                mention = text[entity.offset: entity.offset + entity.length].lower()
                if mention == "@serenaaichatbot":
                    is_entity_mention = True

    # 🔹 Reply to bot
    is_reply_to_bot = bool(
        reply_to
        and reply_to.from_user
        and reply_to.from_user.id == config.serena_id
    )

    # =========================
    # 🚀 Decide to Reply
    # =========================
    should_reply = (
        chat_type == enums.ChatType.PRIVATE
        or is_username_mention
        or is_entity_mention
        or is_name_mention
        or is_reply_to_bot
    )

    if not should_reply:
        return

    print(
        f"[SERENA] chat={chat_id} type={chat_type} text={text} "
        f"name={is_name_mention} user={is_username_mention} "
        f"entity={is_entity_mention} reply={is_reply_to_bot}"
    )

    # =========================
    # 🤖 Generate Reply
    # =========================
    try:
        await client.send_chat_action(chat_id, enums.ChatAction.TYPING)

        await serena_react(client, message)

        ai_reply = await ask_serena(message)
        reply_text = ai_reply.get("reply", "I couldn't generate a reply.")

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
