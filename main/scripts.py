
import config
import requests


def groq(messages: list = None, api_key: str = None):  # messages: [{'role': 'user', 'content': 'Hello!'}]
    if messages is None:
        messages = []

    if messages and messages[0].get('role') != "system":
        messages.insert(0, {"role": "system", "content": config.AI_SYS_TXT})

    data = {
        "model": "llama-3.1-8b-instant",
        "messages": messages
    }

    if api_key is None:
        api_key = getattr(config, "groq_api_key", None)
    if not api_key:
        return {'error': 'missing api_key'}

    headers = {"Authorization": f"Bearer {api_key}"}
    api_url = "https://api.groq.com/openai/v1/chat/completions"

    try:
        result = requests.post(api_url, json=data, headers=headers)
        if result.status_code != 200:
            return {'error': f'{result.status_code} {result.reason}: {result.text}'}
        results = result.json()
        return {'reply': results.get("choices", [{}])[0].get("message", {}).get("content", "*🥲 Sorry, no response.*")}
    except Exception as e:
        return {'error': str(e)}
