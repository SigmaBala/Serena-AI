<div align="center">

![Serena AI Banner](https://hebbkx1anhila5yf.public.blob.vercel-storage.com/serena-Exhp7AFIr1UC8Bdb1XwhXHedLvsAzW.png)

# Serena AI

### *Your Smart Companion on Telegram* 💖

> Advanced AI Chatbot for Smart Conversations, Stickers, Group Management & More!

[![License](https://img.shields.io/badge/License-Apache_2.0-E91E63?style=for-the-badge)](https://opensource.org/licenses/Apache-2.0)
[![Python](https://img.shields.io/badge/Python-3.8+-E91E63?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Telegram](https://img.shields.io/badge/Telegram-Bot_API-E91E63?style=for-the-badge&logo=telegram)](https://core.telegram.org/bots/api)
[![Groq AI](https://img.shields.io/badge/Groq-LLaMA_3.1-E91E63?style=for-the-badge)](https://groq.com/)
[![MongoDB](https://img.shields.io/badge/MongoDB-Database-E91E63?style=for-the-badge&logo=mongodb)](https://www.mongodb.com/)

</div>

---

## ✨ Key Features

<div align="center">
  <table>
    <tr>
      <td align="center" width="50%">
        <h3>💬 AI Conversations</h3>
        <p>Powered by Groq LLaMA 3.1 8B<br/>Lightning-fast intelligent responses</p>
      </td>
      <td align="center" width="50%">
        <h3>🎭 Sticker Reactions</h3>
        <p>Smart & Random Sticker Responses<br/>Expressive visual communication</p>
      </td>
    </tr>
    <tr>
      <td align="center">
        <h3>👥 Group Management</h3>
        <p>Enable/Disable Bot in Groups<br/>Admin controls made simple</p>
      </td>
      <td align="center">
        <h3>⚡ Developer Tools</h3>
        <p>Broadcast to Users & Groups<br/>Advanced admin features</p>
      </td>
    </tr>
    <tr>
      <td align="center">
        <h3>💾 Persistent Storage</h3>
        <p>MongoDB Database<br/>Never lose your chat history</p>
      </td>
      <td align="center">
        <h3>💖 Smart Reactions</h3>
        <p>Auto Emoji Reactions<br/>Feel the love in every chat</p>
      </td>
    </tr>
  </table>
</div>

---

## 🚀 Quick Start

### What You'll Need

- Python 3.8+
- Telegram Bot Token from [@BotFather](https://t.me/BotFather)
- Groq API Key from [groq.com](https://groq.com)
- MongoDB database (free tier available at [MongoDB Atlas](https://www.mongodb.com/cloud/atlas))

### Installation

```bash
# Clone the repository
git clone https://github.com/sigmabala/serena-ai.git
cd serena-ai

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create config.py with your credentials (see below)

# Run the bot
python3 -m main
```

💡 **Pro Tip:** Use `screen -R serena-ai` to keep the bot running in the background!

---

## 📋 Configuration

Create a `config.py` file in the root directory with your credentials:

```python
# config.py - Keep this secure! Never commit to git!

# Telegram Credentials
API_ID = 12345678
API_HASH = "your_api_hash_here"
BOT_TOKEN = "123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11"

# Groq API Key (for LLaMA 3.1 8B inference)
GROQ_API_KEY = "gsk_your_groq_api_key_here"

# MongoDB Connection String
MONGODB_URL = "mongodb+srv://username:password@cluster.mongodb.net/"

# Developer Configuration
developer_ids = [123456789, 987654321]  # Your Telegram user IDs
serena_id = 123456789                   # Bot owner's Telegram ID
```

### Getting Your Credentials

| Credential | How to Get |
|-----------|-----------|
| **API_ID & API_HASH** | Visit [my.telegram.org](https://my.telegram.org) |
| **BOT_TOKEN** | Chat with [@BotFather](https://t.me/BotFather) on Telegram |
| **GROQ_API_KEY** | Sign up at [groq.com](https://groq.com) |
| **MONGODB_URL** | Create free account at [MongoDB Atlas](https://www.mongodb.com/cloud/atlas) |
| **Your Telegram ID** | Message [@userinfobot](https://t.me/userinfobot) |

---

## 📁 Project Layout

```
serena-ai/
├── main/
│   ├── __init__.py           # Package setup
│   ├── __main__.py           # Bot startup
│   ├── serena.py             # Main bot logic
│   ├── database.py           # MongoDB operations
│   └── broadcast.py          # Bulk messaging
├── config.py                 # Your credentials
├── requirements.txt          # Dependencies
├── serena.png                # Banner image
├── LICENSE                   # Apache 2.0
└── README.md                 # This file
```

---

## 🛠 Built With

<div align="center">

| | |
|---|---|
| **Language** | Python 3.8+ |
| **Telegram Framework** | Pyrogram 2.0+ |
| **AI Engine** | Groq LLaMA 3.1 8B |
| **Database** | MongoDB |
| **Async Framework** | asyncio |
| **HTTP Client** | aiohttp / Requests |

</div>

---

## 📚 How to Use

### Quick Links

[Add to Group](https://t.me/ShinchanFilterBot?startgroup=true&admin=manage_chat+delete_messages) • [Chat Now](https://t.me/ShinchanFilterBot) • [Updates](https://t.me/nandhabots)

### Commands

| Command | Usage |
|---------|-------|
| `/start` | Start the bot and see menu options |
| `/chatbot on` | Enable bot in group (group admin only) |
| `/chatbot off` | Disable bot in group (group admin only) |
| `/stats` | View stats (developers only) |
| `/bcast <msg>` | Broadcast to users (developers only) |
| `/gcast <msg>` | Broadcast to groups (developers only) |

### Chatting Tips

**In Private Messages:**
- Send any message to get AI responses
- Share stickers to receive sticker reactions
- Serena remembers your conversation

**In Groups:**
- Mention: `@Serena` or `Serena`
- Reply to Serena's messages
- Admins control bot with `/chatbot on/off`
- Enjoy emoji reactions from Serena

---

## 🤝 Contributing

Found a bug? Have a feature idea? Want to improve docs? We'd love your help!

1. Fork the repo
2. Create a feature branch: `git checkout -b feature/MyFeature`
3. Commit your changes: `git commit -m 'Add MyFeature'`
4. Push to the branch: `git push origin feature/MyFeature`
5. Open a Pull Request

All contributions are welcome - from bug fixes to documentation improvements!

---

## 📞 Community & Support

- **Chat with Serena**: [@SerenaAiChatBot](https://t.me/SerenaAiChatBot)
- **Updates & News**: [@nandhabots](https://t.me/nandhabots)
- **Report Issues**: [GitHub Issues](https://github.com/sigmabala/serena-ai/issues)
- **Discuss Ideas**: [GitHub Discussions](https://github.com/sigmabala/serena-ai/discussions)

---

## 📄 License

Licensed under Apache 2.0 - see [LICENSE](LICENSE) file for details.

---

## 🙏 Thanks To

- [Pyrogram](https://docs.pyrogram.org/) - Telegram client library
- [Groq](https://groq.com/) - Lightning-fast AI inference
- [MongoDB](https://www.mongodb.com/) - Database backend
- All amazing contributors and supporters ❤️

---

<div align="center">

**Made with 💖 for the Telegram Community**

**[⬆ Back to Top](#serena-ai)**

</div>
