from sakura import Client
from main import serena
from main.database import *
from pyrogram import filters, types, enums, errors
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

import config
import random
import re
import requests
import os

developers = [5696053228, 1666544436]

RAN_MSG = [
     "Hi there, I can't reply to that question. Try asking again.",
     "Hello, something went wrong.",
     "Hey, I don't know why you'd ask such a thing.",
     "Hmm... well, I don't know.",
     "Please ask something else."
]

# Fixed: Added missing closing parenthesis
sakuserena = Client(
    username=config.username,
    password=config.password,
    mongo=config.db_url
)

@serena.on_message(filters.command("start") & filters.private)
async def start_command(client, message):
    text = (
        f"Hello {message.from_user.first_name}! ✨\n"
        "I am **Serena**, your advanced AI assistant.\n\n"
        "**Commands:**\n"
        "• `/serena on/off` - Enable/Disable me in groups."
    )
    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("Updates Channel 📢", url="https://t.me/nandhabots")],
        [InlineKeyboardButton("Add Me To Your Group ➕", url=f"https://t.me/{client.me.username}?startgroup=true")]
    ])
    # Fixed: caption -> text
    await message.reply_text(text=text, reply_markup=buttons)

async def serena_react(client, message):
     try:
        # Fixed: Pyrogram reaction syntax
        await serena.send_reaction(
            chat_id=message.chat.id,
            message_id=message.id,
            emoji=random.choice(['🥰', '❤️', '😁', '🗿', '🤗', '🎉', '😎'])
        )
     except Exception:
          pass

async def ask_serena(chat_id, user_id, name, prompt):
     try:
        response = sakuserena.sendMessage(user_id, config.char_id, prompt)
        reply = response['reply']
        reply = re.sub(r'\bUser\b(?!s)', name, reply, flags=re.IGNORECASE)
     except Exception as e: # Fixed: Correct exception handling
           print(f"chat_id: {chat_id}\nUser: {name}\nError: {str(e)}\nPrompt: {prompt}")
           reply = random.choice(RAN_MSG)
     return reply

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

@serena.on_message((filters.text | filters.sticker | filters.animation), group=2)
async def serena_reply(client, message):
    reply_to = message.reply_to_message
    chat_id = message.chat.id
    user = message.sender_chat if message.sender_chat else message.from_user
    name = message.sender_chat.title if message.sender_chat else message.from_user.first_name
    chatname = message.chat.title if message.chat.title else (message.chat.first_name)
     
    # Logic for Mentions
    is_mentioned = message.text and bool(re.search(r'serena|@serenaaichatbot', string=message.text, flags=re.IGNORECASE))
    # Logic for Replies to Bot
    is_reply_to_bot = reply_to and reply_to.from_user and reply_to.from_user.id == config.serena_id
    
    if (is_mentioned or is_reply_to_bot or message.chat.type == enums.ChatType.PRIVATE):
        if message.from_user and (message.from_user.is_bot or message.from_user.id == config.serena_id):
            return

        is_serena_enabled = get_chat_mode(chat_id, chatname)
        if not is_serena_enabled:
             return

        # Handle Stickers/Animations
        if message.sticker or message.animation:
             if message.sticker:
                  add_chat_sticker(chat_id=chat_id, sticker_id=message.sticker.file_id)
             try:
                 stickers = get_all_stickers()
                 if stickers:
                    return await message.reply_sticker(sticker=random.choice(stickers), quote=True)
             except Exception as e:
                   print(f"Sticker Error: {e}")
             return

        # Handle Text
        await client.send_chat_action(chat_id=chat_id, action=enums.ChatAction.TYPING)
        await serena_react(client, message)
        
        ai_reply = await ask_serena(chat_id, user.id, name, message.text)
        return await message.reply_text(text=ai_reply, quote=True)

@serena.on_message(filters.command('serena', prefixes=['.', '?', '/']))
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
         return await message.reply('Usage: `.serena on|off`')

@serena.on_message((filters.me | filters.user(developers)) & filters.command('chats', prefixes=['.', '?', '/']))
async def get_serena_chats(client, message):
       chats = get_chats()
       filename = "SerenaChats.txt"
       text = f'❤️ Total Serena Chats: {len(chats)}\n\n'
       
       # Assuming get_chats returns a list or a specific structure based on your DB
       for i, chat in enumerate(chats):
           text += f"{i+1}. {chat.get('name')} - (`{chat.get('chat_id')}`): {chat.get('chat')}\n"
           
       with open(filename, 'w') as file:
           file.write(text)
           
       await message.reply_document(document=filename, quote=True)
       if os.path.exists(filename):
           os.remove(filename)
