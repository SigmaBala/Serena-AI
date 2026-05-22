from main import mongodb

db = mongodb["chats"]
users = mongodb["users"]
groups = mongodb["groups"]


# ==========================================
# CHAT MODES
# ==========================================

def set_chat_mode(chat_id: int, chatname, mode):
    chat = {"chat_id": str(chat_id)}

    db.update_one(
        chat,
        {
            "$set": {
                "chat": mode,
                "name": chatname,
            }
        },
        upsert=True,
    )

    return True


def get_chats():
    data = []

    for chat in db.find():
        if "chat" in chat:
            data.append(
                {
                    "name": chat.get("name"),
                    "chat_id": chat.get("chat_id"),
                    "chat": chat.get("chat"),
                }
            )

    if len(data) == 0:
        chat_ids = data
    else:
        chat_ids = [x["chat_id"] for x in data]

    return chat_ids, data


def get_chat_mode(chat_id: int, chatname):
    chat = {"chat_id": str(chat_id)}

    if not db.find_one(chat):
        set_chat_mode(chat_id, chatname, False)

    chat_data = db.find_one(chat)

    return chat_data.get("chat", False)


# ==========================================
# STICKERS
# ==========================================

def get_all_stickers():
    all_stickers = []

    for chat in db.find():
        if chat.get("stickers"):
            all_stickers.extend(chat["stickers"])

    return all_stickers


def get_chat_stickers(chat_id: int):
    chat = db.find_one({"chat_id": str(chat_id)})

    if chat and "stickers" in chat:
        return chat["stickers"]

    return []


def add_chat_sticker(chat_id: int, sticker_id):
    chat_key = {"chat_id": str(chat_id)}
    chat = db.find_one(chat_key)

    if not chat:
        db.insert_one(
            {
                "chat_id": str(chat_id),
                "stickers": [sticker_id],
            }
        )
        return True

    stickers = chat.get("stickers", [])

    if sticker_id in stickers:
        return

    db.update_one(
        chat_key,
        {"$push": {"stickers": sticker_id}},
    )

    return True


# ==========================================
# USERS
# ==========================================

def already_db(user_id):
    user = users.find_one({"user_id": str(user_id)})

    return bool(user)


def add_user(user_id):
    if already_db(user_id):
        return

    return users.insert_one({"user_id": str(user_id)})


def remove_user(user_id):
    if not already_db(user_id):
        return

    return users.delete_one({"user_id": str(user_id)})


def all_users():
    return users.count_documents({})


# ==========================================
# GROUPS
# ==========================================

def already_dbg(chat_id):
    group = groups.find_one({"chat_id": str(chat_id)})

    return bool(group)


def add_group(chat_id):
    if already_dbg(chat_id):
        return

    return groups.insert_one({"chat_id": str(chat_id)})


def all_groups():
    return groups.count_documents({})


# ==========================================
# AI MEMORY SYSTEM
# ==========================================

def build_memory_id(chat_id, user_id=None):
    """
    Private Chat:
        memory = chat_id

    Group Chat:
        memory = chat_id:user_id
    """

    is_group = str(chat_id).startswith("-100")

    if is_group and user_id:
        return f"{chat_id}:{user_id}"

    return str(chat_id)


def get_chat_history(chat_id, user_id=None):
    memory_id = build_memory_id(chat_id, user_id)

    chat_data = db.find_one({"chat_id": memory_id})

    if chat_data and "history" in chat_data:
        return chat_data["history"]

    return []


def update_chat_history(chat_id, user_msg, ai_msg, user_id=None):
    memory_id = build_memory_id(chat_id, user_id)

    history = get_chat_history(chat_id, user_id)

    history.append(
        {
            "role": "user",
            "content": user_msg,
        }
    )

    history.append(
        {
            "role": "assistant",
            "content": ai_msg,
        }
    )

    # keep recent messages only
    history = history[-12:]

    db.update_one(
        {"chat_id": memory_id},
        {
            "$set": {
                "history": history,
            }
        },
        upsert=True,
    )
```
