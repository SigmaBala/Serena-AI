
from main import pbot
from main.database import *
from pyrogram import filters, types, enums, errors
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

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

START_GIF = "https://www.image2url.com/r2/default/videos/1776914939431-33d60ca9-688f-4fc3-aa76-984bf7116773.mp4"

START_BUTTONS = InlineKeyboardMarkup([
        [InlineKeyboardButton("Add Me To Your Group ➕", url="https://t.me/nandhabots", style=enums.ButtonStyle.PRIMARY)],
        [InlineKeyboardButton("Updates Channel 📢", url=f"https://t.me/SerenaAIChatBot?startgroup=true", style=enums.ButtonStyle.PRIMARY)],
        [InlineKeyboardButton("About ℹ️", callback_data='about', style=enums.ButtonStyle.PRIMARY)]
    ])


KB_BUTTONS = InlineKeyboardMarkup([
        [InlineKeyboardButton("Add Me To Your Group ➕", url=f"https://t.me/SerenaAIChatBot?startgroup=true")],
        [InlineKeyboardButton("Updates Channel 📢", url="https://t.me/nandhabots")], 
        [InlineKeyboardButton("About ℹ️", callback_data='about')]
    ])


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

    text = (
        f"Hello {message.from_user.mention}! ✨\n"
        "I am **Serena**, advanced AI assistant.\n"
        "I'm here to help make things a little easier.\n\n"
        "**Commands:**\n"
        "• `/chatbot on/off` - Enable/Disable me in groups."
    )

    
    await message.reply_animation(
        animation=START_GIF, 
        caption=text, 
        reply_markup=START_BUTTONS
    )


ABOUT_TEXT = """
Hello! My name is **Serena AI**, and I'm an artificial intelligence designed to provide helpful and clear explanations. 

As a conversational AI, I'm always ready to assist with any questions or topics you'd like to discuss, I aim to make complex concepts accessible and facilitate meaningful interactions.
"""

@pbot.on_callback_query(filters.regex("about"))
async def about(_, query: CallbackQuery):
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("Source Code 📁", url="https://github.com/SigmaBala/Serena-AI")],
        [InlineKeyboardButton("🔙 Back", callback_data="start_back")]
    ])

    await query.message.edit_caption(
        caption=ABOUT_TEXT,
        reply_markup=kb
    )

@pbot.on_callback_query(filters.regex("start_back"))
async def back_to_start(_, query: CallbackQuery):
    text = (
        f"Hello {query.from_user.mention}! ✨\n"
        "I am **Serena**, advanced AI assistant.\n"
        "I'm here to help make things a little easier.\n\n"
        "**Commands:**\n"
        "• `/chatbot on/off` - Enable/Disable me in groups."
    )
    
    await query.message.edit_caption(
        caption=text,
        reply_markup=KB_BUTTONS
    )
    

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
    try:
        # 1. Set action immediately
        await client.send_chat_action(chat_id, enums.ChatAction.CHOOSE_STICKER)
        
        if message.sticker:
            add_chat_sticker(chat_id=chat_id, sticker_id=message.sticker.file_id)

        # 2. Get stickers from database/list
        stickers = get_all_stickers()
        
        # Check if stickers list is not empty
        if stickers:
            random_sticker = random.choice(stickers)
            
            # 3. Use specific method based on context
            if is_pm:
                await client.send_sticker(chat_id, random_sticker)
            else:
                await message.reply_sticker(random_sticker)
            
            return

    except Exception as e:
        print(f"Sticker processing error: {e}")
    
    return
  

# =========================
# 🧠 AI Text Processing
# =========================
try:
    # 2. Update action to TYPING for text responses
    await client.send_chat_action(chat_id, enums.ChatAction.TYPING)
    
    await serena_react(client, message)

    ai_reply = await ask_serena(message)
    reply_text = ai_reply.get("reply", "I couldn't generate a reply.")

    if is_pm:
        return await client.send_message(chat_id, reply_text)
    return await message.reply_text(reply_text)

except Exception as e:
    print(f"Serena reply error: {e}")
  
    error_msg = "Something went wrong while generating a reply."
    if is_pm:
        await client.send_message(chat_id, error_msg)
    else:
        await message.reply_text(error_msg)




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
