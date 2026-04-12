from pyrogram import Client, filters
from pyrogram.types import Message
import requests
import config

# --- The logic adapted for Pyrogram ---

@Client.on_message(filters.command("ai") & filters.private)
async def groq_chat(client: Client, message: Message):
    # 1. Provide immediate feedback to the user
    status_msg = await message.reply("*Thinking...*")
    
    # 2. Prepare the messages list
    # For a simple one-off chat:
    messages = [
        {"role": "system", "content": config.AI_SYS_TXT},
        {"role": "user", "content": message.text.split(None, 1)[1] if len(message.command) > 1 else "Hello!"}
    ]

    # 3. Groq API Configuration
    api_key = getattr(config, "groq_api_key", None)
    if not api_key:
        await status_msg.edit("❌ Error: Missing API Key in config.")
        return

    data = {
        "model": "llama-3.1-8b-instant",
        "messages": messages
    }
    headers = {"Authorization": f"Bearer {api_key}"}
    api_url = "https://api.groq.com/openai/v1/chat/completions"

    # 4. Perform the request
    try:
        # Note: Using requests.post is synchronous and can block the bot. 
        # For production, consider 'httpx' or 'aiohttp'.
        result = requests.post(api_url, json=data, headers=headers)
        
        if result.status_code != 200:
            await status_msg.edit(f"⚠️ Error: {result.status_code}\n`{result.text[:100]}`")
            return

        response_data = result.json()
        reply_text = response_data.get("choices", [{}])[0].get("message", {}).get("content", "*🥲 Sorry, no response.*")

        # 5. Send the final answer back to Telegram
        await status_msg.edit(reply_text)

    except Exception as e:
        await status_msg.edit(f"❌ Exception: {str(e)}")
