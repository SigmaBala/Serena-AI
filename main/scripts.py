
import requests
import config


def get_groq_response(user_text):
    """Core logic to fetch response from Groq"""
    api_key = getattr(config, "groq_api_key", None)
    if not api_key:
        return "❌ Error: Missing API Key in config."

    # Construct messages list with system prompt
    messages = [
        {"role": "system", "content": config.AI_SYS_TXT},
        {"role": "user", "content": user_text}
    ]

    data = {
        "model": "llama-3.1-8b-instant",
        "messages": messages
    }
    
    headers = {"Authorization": f"Bearer {api_key}"}
    api_url = "https://api.groq.com/openai/v1/chat/completions"

    try:
        response = requests.post(api_url, json=data, headers=headers)
        if response.status_code != 200:
            return f"⚠️ Error: {response.status_code} - {response.text}"
        
        result = response.json()
        return result.get("choices", [{}])[0].get("message", {}).get("content", "*🥲 Sorry, no response.*")
    except Exception as e:
        return f"🆘 Exception: {str(e)}"
