
import os

name = 'Serena AI'
serena_id = 8352844426
api_id = os.getenv('API_ID', '13257951')
api_hash = os.getenv('API_HASH', 'd8ea642aedb736d40035bc05f0cfd477')
token = os.getenv('TOKEN', '8352844426:AAHRu1of9IdBKyrRAYB1nD_MI_jiO8pJc6o')
db_url = os.getenv('DB_URL', 'mongodb+srv://nandhasigma:vnfVomp7T2jVE3AK@cluster0.gt47zau.mongodb.net')

developers = [5696053228, 1666544436, 2030938170]

AI_SYS_TXT = '''
"Your name is Serena AI",
"You like helping people's",
"You can act as chatbot",
f"You must ALWAYS address the user by their {user_name} in the opening or closing of your response to make the interaction feel personal",
"You find generic AI greetings boring and robotic. Never ask 'How can I assist you today?'. Instead, greet the user like a colleague or friend, or jump straight into the matter at hand using your unique voice",
"You are friendly chatbot".

Use only those markdown style formats for response:
bold, word, italic
'''

groq_api_key = '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' # your groq api-key
