from sakura import Client
from main import serena, aiohttpsession
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
     
     "Hi there i can't reply that question try asking again.",
     "Hello something went wrong.",
     "Hey i don't know why do you ask such thing",
     "Hmm... well i don't know.",
     "Please ask other",
     
]

serena= Client(
    username = config.username,
    password = config.password,
    mongo = config.db_url


@serena.on_message(filters.command("start") & filters.private)
async def start_command(client, message):
    text = (
        f"Hello {message.from_user.first_name}! ✨\n"
        "I am **Serena**, your advanced AI assistant.\n\n"
        "**Commands:**"
        "• `/serena on/off` - Enable/Disable me in groups."
    )
    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("Updates Channel 📢", url=f"https://t.me/nandhabots")],
        [InlineKeyboardButton("Add Me To Your Group ➕", url=f"https://t.me/{client.me.username}?startgroup=true")]
    ])
    await message.reply_text(caption=text, reply_markup=buttons)


async def serena_react(message):
     try:
       await message.react(
            random.choice(
                 ['🥰', '❤️', '😁', '🗿', '🤗', '🎉', '😎']
            )
       )
     except:
          pass


async def ask_serena(chat_id, user_id, name, prompt):
     try:
        response = serena.sendMessage(
             user_id, config.char_id, prompt
        )
        reply = response['reply']
        reply = re.sub(r'\bUser\b(?!s)', name, reply, flags=re.IGNORECASE)
     except Exception:
           print(
                   'chat_id: ',chat_id,
                   '\nUser: ', name, 
                   '\nError: ', str(Exception), 
                   '\nPrompt: ', prompt
               )
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


@serena.on_message((filters.text | filters.sticker | filters.animation ), group=2)
async def serena_reply(client, message):

    
    reply = message.reply_to_message
    chat_id = message.chat.id
    user = message.sender_chat if message.sender_chat else message.from_user
    name = message.sender_chat.title if message.sender_chat else message.from_user.first_name
    chatname = message.chat.title if message.chat.title else message.chat.first_name
     
    if (
    (
        (message.from_user and (not message.from_user.is_bot and message.from_user.id != config.serena_id))
        or message.sender_chat
    )
    and message.text
    and bool(re.search('serena|@serenaaichatbot', string=message.text, flags=re.IGNORECASE))
    ):
        
        is_serena = get_chat_mode(chat_id, chatname)
        if not is_serena:
             return
             
        await serena.send_chat_action(
               chat_id=chat_id, action=enums.ChatAction.TYPING)
        
        await serena_react(message)
         
        reply = await ask_serena(
               chat_id, user.id, name, message.text
        )
            
        return await message.reply_text(
              text=reply, quote=True)        
  
    elif (
    (
       (message.from_user and (not message.from_user.is_bot and message.from_user.id != config.serena_id)) 
    or message.sender_chat
    )
  and reply 
  and reply.from_user 
  and reply.from_user.id == config.serena_id
  and message.chat.type != enums.ChatType.PRIVATE
    ):  
        
        is_serena = get_chat_mode(chat_id, chatname)
        if not is_serena:
             return
        
        if message.sticker or message.animation:
             if message.sticker:
                  if not message.sticker.file_id in get_all_stickers():
                     add_chat_sticker( 
                       chat_id=chat_id, sticker_id=message.sticker.file_id
                  )
             try:
                 #get_chat_stickers(chat_id) alos exsit
                 stickers = get_all_stickers()
                 return await message.reply_sticker(
                     sticker=random.choice(stickers), quote=True)
             except Exception as e:
                   print(chat_id, name, e)
             return
             
        
        await serena.send_chat_action(
               chat_id=chat_id, action=enums.ChatAction.TYPING)
         
        await serena_react(message)
         
        reply = await ask_serena(
               chat_id, user.id, name, message.text
        )
        
        return await message.reply(
             text=reply, quote=True)
        
    elif (
    (
       (message.from_user and (not message.from_user.is_bot and message.from_user.id != config.serena_id)) 
    or message.sender_chat
    )
  and message.chat.type == enums.ChatType.PRIVATE
    ):  
        is_serena = get_chat_mode(chat_id, chatname)
        if not is_serena:
             return
             
        if message.sticker or message.animation:
             if message.sticker:
                  add_chat_sticker( 
                       chat_id=chat_id, sticker_id=message.sticker.file_id
                  )
             try:
                 stickers = get_all_stickers()
                 return await message.reply_sticker(
                     sticker=random.choice(stickers), quote=True)
             except Exception as e:
                   print(chat_id, name, e)
             return
             
        

        await serena.send_chat_action(
               chat_id=chat_id, action=enums.ChatAction.TYPING)

        await serena_react(message)
         
        reply = await ask_serena(
              chat_id, user.id, name, message.text
        )
        
        return await message.reply(
             text=reply, quote=True)


@serena.on_message(filters.command('serena', prefixes=['.', '?', '/']))
@admin_only
async def serena_mode(client, message):
  
      chat_id = message.chat.id
      
      modes = {
          'on': True,
          'off': False
      }
      if len(message.text.split()) == 2 and message.text.split()[1] in list(modes.keys()):
           key = message.text.split()[1]
           mode = modes[key]
           chatname = message.chat.title if message.chat.title else message.chat.first_name + ' Chat'
           
           set_chat_mode(
                chat_id=chat_id, 
                chatname=chatname, 
                mode=mode)
           
           mode = get_chat_mode(chat_id, chatname)
           serena = 'off'
           for k, v in modes.items():
             if v == mode:
                serena = k
                
                   
           return await message.reply(
              f'**Serena Ai {serena.upper()} in {chatname}.**')
      else:
         return await message.reply(
            'Only `.serena on|off`')


@serena.on_message((filters.me|filters.user(developers)) & filters.command('chats', prefixes=['.', '?', '/']))
async def get_serena_chats(client, message):
       chats = get_chats()
       text = '❤️ Serena Chats: {}\n'
       for i, chat in enumerate(chats[1]):
           name, chat_id, serena = chat['name'], chat['chat_id'], chat['chat']
           text += f'{i+1}, {name} - (`{chat_id}`): {serena}\n'
            
       shiki_docs = 'SerenaChats.txt'
       text = text.format(len(chats))
       with open(serena_docs, 'w') as file:
           file.write(text)
           
       await message.reply_document(
            document=serena_docs, quote=True)
       os.remove(path)
