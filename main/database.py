
from main import mongodb 

# Define your collections
users_col = mongodb["users"]
groups_col = mongodb["groups"]
chat_history_col = mongodb["chat_history"]
settings_col = mongodb["settings"]
stickers_col = mongodb["stickers"]

# ==========================================
# 🧠 DATABASE FUNCTIONS
# ==========================================

def add_user(user_id: int):
    if not users_col.find_one({"user_id": user_id}):
        users_col.insert_one({"user_id": user_id})

def add_group(chat_id: int):
    if not groups_col.find_one({"chat_id": chat_id}):
        groups_col.insert_one({"chat_id": chat_id})

def get_chat_mode(chat_id: int, chat_name: str) -> bool:
    chat = settings_col.find_one({"chat_id": chat_id})
    if chat:
        return chat.get("chatbot_mode", False)
    return False

def set_chat_mode(chat_id: int, chatname: str, mode: bool):
    settings_col.update_one(
        {"chat_id": chat_id},
        {"$set": {"chatbot_mode": mode, "chat_name": chatname}},
        upsert=True
    )

def add_chat_sticker(chat_id: int, sticker_id: str):
    stickers_col.update_one(
        {"chat_id": chat_id},
        {"$addToSet": {"stickers": sticker_id}}, # $addToSet prevents duplicates
        upsert=True
    )

def get_all_stickers():
    all_stickers = []
    # Get all documents in the stickers collection
    for doc in stickers_col.find():
        all_stickers.extend(doc.get("stickers", []))
    return list(set(all_stickers))

# --- History Functions ---
def update_chat_history(chat_id: int, user_text: str, bot_reply: str, user_id: int):
    key = f"{chat_id}_{user_id}"
    
    # Fetch existing history
    doc = chat_history_col.find_one({"_id": key})
    history = doc["history"] if doc else []
    
    # Append new messages
    history.append({"role": "user", "content": user_text})
    history.append({"role": "assistant", "content": bot_reply})
    
    # Keep only the last 10 messages
    history = history[-50:]
    
    # Save back to database
    chat_history_col.update_one(
        {"_id": key},
        {"$set": {"history": history}},
        upsert=True
    )

def get_chat_history(chat_id: int, user_id: int) -> list:
    key = f"{chat_id}_{user_id}"
    doc = chat_history_col.find_one({"_id": key})
    if doc:
        return doc.get("history", [])
    return []
