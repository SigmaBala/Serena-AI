
import os
import random
import re
from typing import Dict, Any

import httpx
from pyrogram import client, enums, errors, filters, types
from pyrogram.enums import ChatType
from pyrogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup

import config
from main import pbot
from main.database import *

# ==========================================
# 📊 CONSTANTS & MARKUPS
# ==========================================

START_STICKERS = [
    "CAACAgUAAxkBAAEBrV9nWukpft8gmtrZVMkbO4GKlZy0HQACWxUAAnHv2FZkjr7WjG3OjzYE",
    "CAACAgIAAx0CZEWBuAACY1Vp5HITx1GrYTA6UcS09fEySVjoewACXxcAAjqz6UmnEUA60wg8cDsE",
    "CAACAgUAAxkBAAEBrWJnWulBrVl7pq-QRI1QCaMjd6laLAAC2RYAAojK2Va2m-0pJ2vqLzYE",
]

START_GIF = "https://www.image2url.com/r2/default/videos/1776914939431-33d60ca9-688f-4fc3-aa76-984bf7116773.mp4"

START_BUTTONS = InlineKeyboardMarkup(
    [
        [
            InlineKeyboardButton(
                "Add Me To Your Group ➕",
                url="http://t.me/ShinchanFilterBot?startgroup=true&admin=manage_chat+delete_messages",
                style=enums.ButtonStyle.DANGER,
            )
        ],
        [
            InlineKeyboardButton(
                "Updates Channel 📢",
                url="https://t.me/nandhabots",
                style=enums.ButtonStyle.PRIMARY,
            ),
            InlineKeyboardButton(
                "About ℹ️",
                callback_data="about",
                style=enums.ButtonStyle.PRIMARY,
            ),
        ],
    ]
)

ABOUT_TEXT = (
    "Hello! My name is **Serena AI**, and I'm an artificial intelligence designed to chatting and provide useful information.\n\n"
    "As a conversational AI, I'm always ready to assist with any questions or topics you'd like to discuss and I aim to make complex concepts accessible and facilitate meaningful interactions."
)

# ==========================================
# 🛠️ DECORATORS & UTILS
# ==========================================


def admin_only(func):
    async def wrapped(client, message):
        user_id = message.from_user.id
        chat_id = message.chat.id

        if message.chat.type in (enums.ChatType.PRIVATE, enums.ChatType.BOT):
            return await func(client, message)

        try:
            user = await client.get_chat_member(chat_id, user_id)

            is_owner = user_id == config.serena_id
            is_dev = (
                user_id in config.developers
                if isinstance(config.developers, list)
                else user_id == config.developers
            )
            is_admin = user.privileges is not None

            if is_admin or is_owner or is_dev:
                return await func(client, message)
            
            return await message.reply_text(
                "❌ This command is only for administrators."
            )

        except errors.ChatAdminRequired:
            return await message.reply_text("**Hello, make me an admin 🥰**")
        except Exception as e:
            print(f"Admin Check Error: {e}")

    return wrapped


async def serena_react(client, message):
    try:
        await pbot.send_reaction(
            chat_id=message.chat.id,
            message_id=message.id,
            emoji=random.choice(["🥰", "❤️", "😁", "🗿", "🤗", "🎉", "😎"]),
        )
    except Exception:
        pass


async def ask_serena(chat_id: int, user_text: str, user_name: str) -> Dict[str, str]:
    # Ensure name contains zero markdown markers or username elements
    clean_name = re.sub(r'[*_`\[\]()@]', '', user_name).strip()
    if not clean_name or clean_name.lower() in ["user", "unknown", "none"]:
        clean_name = "Friend"

    # Deep clean incoming user text so the AI doesn't see lingering usernames in PMs
    cleaned_user_text = re.sub(r'@\w+', clean_name, user_text)

    raw_history = get_chat_history(chat_id)
    history = []

    # Clean historical entries to prevent legacy format imitation
    if raw_history and isinstance(raw_history, list):
        for msg in raw_history:
            if isinstance(msg, dict) and "content" in msg:
                cleaned_content = re.sub(r'@\w+', clean_name, msg["content"])
                history.append({"role": msg.get("role", "user"), "content": cleaned_content})
            else:
                history.append(msg)

    # Re-verify layout template modifications inside config variables
    base_sys = getattr(config, "AI_SYS_TXT", "You are Serena, an AI assistant.")
    personalized_sys_prompt = base_sys.replace("{user_name}", clean_name).replace("[user_name]", clean_name)

    # Rigid structural ruleset injection
    strict_formatting_rule = (
        f"\n\n[CRITICAL OPERATIONAL DIRECTIVE]: You are in a private chat with {clean_name}. "
        f"Do NOT invent or utilize username tags beginning with '@'. "
        f"Address the person only as '{clean_name}' naturally within your sentences. "
        f"Never output '@' formats."
    )
    
    final_system_prompt = personalized_sys_prompt + strict_formatting_rule

    messages = [{"role": "system", "content": final_system_prompt}]
    messages.extend(history)
    messages.append({"role": "user", "content": cleaned_user_text})

    headers = {"Authorization": f"Bearer {config.groq_api_key}"}
    data = {"model": "llama-3.1-8b-instant", "messages": messages}

    try:
        async with httpx.AsyncClient() as async_client:
            res = await async_client.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers=headers,
                json=data,
                timeout=15.0,
            )

        if res.status_code == 200:
            answer = res.json()["choices"][0]["message"]["content"]
            
            # Post-processing interception: Replace accidental AI username output with the clean name
            answer = re.sub(r'@\w+', clean_name, answer)
            
            update_chat_history(chat_id, cleaned_user_text, answer)
            return {"reply": answer}
        
        return {"reply": "⚠️ Error connecting to AI."}
    except httpx.TimeoutException:
        return {"reply": "⏳ AI request timed out. Please try again."}
    except Exception as e:
        return {"reply": f"❌ An unexpected error occurred: {e}"}


# ==========================================
# 🚀 COMMANDS & CALLBACKS
# ==========================================


@pbot.on_message(filters.command("start"))
async def start_command(client, message):
    if message.chat.type == ChatType.PRIVATE:
        add_user(message.from_user.id)
        try:
            await client.send_sticker(
                chat_id=message.chat.id, sticker=random.choice(START_STICKERS)
            )
        except Exception as e:
            print(f"Start Sticker Error: {e}")

    text = (
        f"Hello {message.from_user.mention}! ✨\n"
        "I am **Serena**, advanced AI assistant.\n"
        "I'm here to help make things a little easier.\n\n"
        "**Commands:**\n"
        "• `/chatbot on/off` - Enable/Disable me in groups."
    )

    await message.reply_animation(
        animation=START_GIF, caption=text, reply_markup=START_BUTTONS
    )


@pbot.on_callback_query(filters.regex("about"))
async def about(_, query: CallbackQuery):
    kb = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "Source Code 📁",
                    url="https://github.com/SigmaBala/Serena-AI",
                    style=enums.ButtonStyle.DANGER,
                )
            ],
            [
                InlineKeyboardButton(
                    "🔙 Back",
                    callback_data="start_back",
                    style=enums.ButtonStyle.PRIMARY,
                )
            ],
        ]
    )

    await query.message.edit_caption(caption=ABOUT_TEXT, reply_markup=kb)


@pbot.on_callback_query(filters.regex("start_back"))
async def back_to_start(_, query: CallbackQuery):
    text = (
        f"Hello {query.from_user.mention}! ✨\n"
        "I am **Serena**, advanced AI assistant.\n"
        "I'm here to help make things a little easier.\n\n"
        "**Commands:**\n"
        "• `/chatbot on/off` - Enable/Disable me in groups."
    )

    await query.message.edit_caption(caption=text, reply_markup=START_BUTTONS)


# ==========================================
# 🧠 CORE ROUTERS & LOGIC
# ==========================================


@pbot.on_message(
    (filters.text | filters.caption | filters.sticker | filters.animation)
    & ~filters.bot,
    group=2,
)
async def serena_reply(client, message):
    chat_id = message.chat.id
    chat_type = message.chat.type
    chat_name = message.chat.title or getattr(message.chat, "first_name", "Chat") or "Private Chat"
    reply_to = message.reply_to_message

    if message.from_user:
        if message.from_user.is_bot or message.from_user.id == client.me.id:
            return
    else:
        return

    text = (message.text or message.caption or "").strip()
    text_lower = text.lower()
    is_pm = chat_type == enums.ChatType.PRIVATE
    
    # Check if the bot was mentioned or replied to
    is_mentioned = (
        "serena" in text_lower
        or f"@{client.me.username.lower()}" in text_lower
        or (
            reply_to
            and reply_to.from_user
            and reply_to.from_user.id == client.me.id
        )
    )

    if not is_pm:
        if not is_mentioned or not get_chat_mode(chat_id, chat_name):
            return

    # Handle Media Interactions
    if message.sticker or message.animation:
        try:
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
            print(f"Sticker Processing Error: {e}")
            return

    # Handle Standard Text Interactions
    try:
        await client.send_chat_action(chat_id, enums.ChatAction.TYPING)
        await serena_react(client, message)

        # 🔧 FIX: Correctly determine who the bot should address
        target_user = message.from_user
        
        # If this is a group reply to someone else (not the bot itself), address the person being replied to
        if reply_to and reply_to.from_user and reply_to.from_user.id != client.me.id:
            target_user = reply_to.from_user

        # Force clean name extraction without formatting strings
        name = "Friend"
        if target_user:
            raw_name = target_user.first_name or target_user.username or "Friend"
            name = re.sub(r'[*_`\[\]()@]', '', raw_name).strip()
            if not name or name.lower() in ["none", "unknown"]:
                name = "Friend"

        ai_reply = await ask_serena(chat_id, text, name)
        reply_text = ai_reply.get("reply", "I couldn't generate a reply.")

        if is_pm:
            await client.send_message(chat_id, reply_text)
        else:
            await message.reply_text(reply_text)

    except Exception as e:
        print(f"Serena core reply error: {e}")


@pbot.on_message(filters.command("chatbot", prefixes=[".", "?", "/"]))
@admin_only
async def serena_mode(client, message):
    chat_id = message.chat.id
    modes = {"on": True, "off": False}

    args = message.text.split()
    if len(args) == 2 and args[1].lower() in modes:
        key = args[1].lower()
        mode_val = modes[key]
        chatname = message.chat.title or (
            getattr(message.chat, "first_name", "Chat") or "Group"
        )

        set_chat_mode(chat_id=chat_id, chatname=chatname, mode=mode_val)
        return await message.reply(
            f"**Serena AI {key.upper()} in {chatname}.**"
        )
    
    return await message.reply("Usage: `/chatbot on|off`")


@pbot.on_message(filters.new_chat_members)
async def new_chat(_, message):
    bot_id = (await pbot.get_me()).id
    add_group(message.chat.id)
    for member in message.new_chat_members:
        if member.id == bot_id:
            await message.reply(
                "🙋‍♂️ Thanks for adding me !\n\nUse `/chatbot on` to keep chatting me ❤️"
            )
          
