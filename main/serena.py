
from main import pbot
from main.database import *
from pyrogram.enums import ChatType
from pyrogram import filters, types, enums, errors
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

import config
import random
import re
import requests
import os


START_STICKERS = [
  "CAACAgUAAxkBAAEBrV9nWukpft8gmtrZVMkbO4GKlZy0HQACWxUAAnHv2FZkjr7WjG3OjzYE",
  "CAACAgIAAx0CZEWBuAACY1Vp5HITx1GrYTA6UcS09fEySVjoewACXxcAAjqz6UmnEUA60wg8cDsE",
  "CAACAgUAAxkBAAEBrWJnWulBrVl7pq-QRI1QCaMjd6laLAAC2RYAAojK2Va2m-0pJ2vqLzYE"
]

START_GIF = "https://www.image2url.com/r2/default/videos/1776914939431-33d60ca9-688f-4fc3-aa76-984bf7116773.mp4"

START_BUTTONS = InlineKeyboardMarkup([
        [
          InlineKeyboardButton("Add Me To Your Group ➕", url="https://t.me/SerenaAIChatBot?startgroup=true", style=enums.ButtonStyle.DANGER)
        ],
        [
          InlineKeyboardButton("Updates Channel 📢", url="https://t.me/nandhabots", style=enums.ButtonStyle.PRIMARY),
          InlineKeyboardButton("About ℹ️", callback_data='about', style=enums.ButtonStyle.PRIMARY)
        ]
    ])


@pbot.on_message(filters.command("start"))
async def start_command(client, message):
    if message.chat.type == ChatType.PRIVATE:
        add_user(message.from_user.id)
        chat_id = message.chat.id
        try:
            await client.send_sticker(
                chat_id=chat_id,
                sticker=random.choice(START_STICKERS)
            )
          
        except Exception as e:
            print(f"Error: {e}")

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
Hello! My name is **Serena AI**, and I'm an artificial intelligence designed to provide helpful and clear explanations.\n 
As a conversational AI, I'm always ready to assist with any questions or topics you'd like to discuss and i aim to make complex concepts accessible and facilitate meaningful interactions.
"""

@pbot.on_callback_query(filters.regex("about"))
async def about(_, query: CallbackQuery):
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("Source Code 📁", url="https://github.com/SigmaBala/Serena-AI", style=enums.ButtonStyle.DANGER)],
        [InlineKeyboardButton("🔙 Back", callback_data="start_back", style=enums.ButtonStyle.PRIMARY)]
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
        reply_markup=START_BUTTONS
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
         

async def ask_serena(prompt, context_text=""):
    # Build a prompt that includes the context of the replied-to message or file
    full_content = f"Context/Memory: {context_text}\n\nUser Question: {prompt}" if context_text else prompt
    
    messages = [
        {"role": "system", "content": config.AI_SYS_TXT},
        {"role": "user", "content": full_content}
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
            return {'reply': res.json()["choices"][0]["message"]["content"]}
        return {'reply': '⚠️ Error connecting to AI.'}
    except Exception as e:
        return {'reply': f"❌ {e}"}



     
def admin_only(func):
    async def wrapped(client, message):
        user_id = message.from_user.id
        chat_id = message.chat.id
        
        if message.chat.type in (enums.ChatType.PRIVATE, enums.ChatType.BOT):
            return await func(client, message)

        try:
            user = await client.get_chat_member(chat_id, user_id)
            
            is_owner = user_id == config.serena_id
            is_dev = user_id in config.developers if isinstance(config.developers, list) else user_id == config.developers
            is_admin = user.privileges is not None

            if is_admin or is_owner or is_dev:
                return await func(client, message)
            else:
                return await message.reply_text("❌ This command is only for administrators.")

        except errors.ChatAdminRequired:
            return await message.reply_text("**Hello, make me an admin 🥰**")
        except Exception as e:
            print(f"Error: {e}")
            
    return wrapped


@pbot.on_message(
    (filters.text | filters.caption | filters.photo | filters.document | filters.sticker | filters.animation) & ~filters.bot,
    group=2
)
async def serena_reply(client, message):
    chat_id = message.chat.id
    reply_to = message.reply_to_message
    
    # 1. Permission & Mention Checks
    if not (message.chat.type == enums.ChatType.PRIVATE or 
            "serena" in (message.text or message.caption or "").lower() or 
            (reply_to and reply_to.from_user and reply_to.from_user.id == client.me.id)):
        return

    # 2. Extract Conversation Memory (Reply Logic)
    context_text = ""
    if reply_to:
        if reply_to.text or reply_to.caption:
            context_text = f"Previous Message: {reply_to.text or reply_to.caption}"
        elif reply_to.photo:
            context_text = f"Replying to a Photo with caption: {reply_to.caption or 'None'}"
        elif reply_to.document:
            context_text = f"Replying to a Document: {reply_to.document.file_name}"

    # 3. Handle Current Media (If message itself is an image/doc)
    current_prompt = message.text or message.caption or "Analyze this file."
    
    # Optional: Image/Doc Analysis Trigger
    # If your AI suite has a vision tool, download and analyze here:
    if message.photo or message.document:
        await client.send_chat_action(chat_id, enums.ChatAction.TYPING)
        # Example: path = await message.download() -> pass to vision AI
        file_info = f" [File: {message.document.file_name if message.document else 'Image'}]"
        current_prompt += file_info

    # 4. Process with AI
    try:
        await client.send_chat_action(chat_id, enums.ChatAction.TYPING)
        await serena_react(client, message)

        ai_response = await ask_serena(current_prompt, context_text)
        reply_text = ai_response.get("reply")

        # 5. Send Response
        if len(reply_text) > 4096:
            # Handle long text by sending as file or splitting
            with open("reply.txt", "w") as f:
                f.write(reply_text)
            await message.reply_document("reply.txt", caption="Result was too long.")
            os.remove("reply.txt")
        else:
            await message.reply_text(reply_text, parse_mode=enums.ParseMode.MARKDOWN)

    except Exception as e:
        print(f"Error in Serena Analysis: {e}")

    # =========================
    # 🎯 Handle Media (Sticker/GIF)
    # =========================
    if message.sticker or message.animation:
        try:
            # Set action ONLY for stickers here
            await client.send_chat_action(chat_id, enums.ChatAction.CHOOSE_STICKER)
            
            if message.sticker:
                add_chat_sticker(chat_id=chat_id, sticker_id=message.sticker.file_id)

            stickers = get_all_stickers()
            if stickers:
                random_sticker = random.choice(stickers)
                if is_pm:
                    await client.send_sticker(chat_id, random_sticker)
                else:
                    await message.reply_sticker(random_sticker)
            return
        except Exception as e:
            print(f"Sticker Error: {e}")
            return




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


@pbot.on_message(filters.new_chat_members)
async def new_chat(_, message):
    bot_id = (await pbot.get_me()).id
    add_group(message.chat.id)
    for member in message.new_chat_members:
        if member.id == bot_id:
            await message.reply("🙋‍♂️ Thanks for adding me !\n\nUse `/chatbot on` to keep chatting me ❤️")
