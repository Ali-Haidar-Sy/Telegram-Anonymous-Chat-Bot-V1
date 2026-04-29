<p align="center">
  <pre>
                                   █████╗ ███╗   ██╗ ██████╗ ███╗   ██╗██╗   ██╗███╗   ███╗ ██████╗ ██╗   ██╗███████╗
                                  ██╔══██╗████╗  ██║██╔═══██╗████╗  ██║╚██╗ ██╔╝████╗ ████║██╔═══██╗██║   ██║██╔════╝
                                  ███████║██╔██╗ ██║██║   ██║██╔██╗ ██║ ╚████╔╝ ██╔████╔██║██║   ██║██║   ██║███████╗
                                  ██╔══██║██║╚██╗██║██║   ██║██║╚██╗██║  ╚██╔╝  ██║╚██╔╝██║██║   ██║██║   ██║╚════██║
                                  ██║  ██║██║ ╚████║╚██████╔╝██║ ╚████║   ██║   ██║ ╚═╝ ██║╚██████╔╝╚██████╔╝███████║
                                  ╚═╝  ╚═╝╚═╝  ╚═══╝ ╚═════╝ ╚═╝  ╚═══╝   ╚═╝   ╚═╝     ╚═╝ ╚═════╝  ╚═════╝ ╚══════╝
        ██████╗██╗  ██╗ █████╗ ████████╗    ██████╗  ██████╗ ████████╗    ██╗   ██╗██╗
       ██╔════╝██║  ██║██╔══██╗╚══██╔══╝    ██╔══██╗██╔═══██╗╚══██╔══╝    ██║   ██║██║
       ██║     ███████║███████║   ██║       ██████╔╝██║   ██║   ██║       ██║   ██║██║
       ██║     ██╔══██║██╔══██║   ██║       ██╔══██╗██║   ██║   ██║       ╚██╗ ██╔╝██║
       ╚██████╗██║  ██║██║  ██║   ██║       ██████╔╝╚██████╔╝   ██║        ╚████╔╝ ███████╗
        ╚═════╝╚═╝  ╚═╝╚═╝  ╚═╝   ╚═╝       ╚═════╝  ╚═════╝    ╚═╝         ╚═══╝  ╚══════╝
  </pre>
</p>

<h1 align="center">🤖 Telegram Anonymous Chat Bot V1<br><sub>Gender‑Aware Stranger Matching on Telegram</sub></h1>

<p align="center">
  <strong>A production‑ready Telegram bot that connects users for private conversations, with smart gender preferences, multi‑language support, and a full admin panel.</strong><br>
  <em>Educational showcase of real‑time matching, SQLite, and the pyTelegramBotAPI library.</em>
</p>

<p align="center">
  <a href="https://github.com/Ali-Haidar-Sy/Telegram-Anonymous-Chat-Bot-V1/stargazers"><img src="https://img.shields.io/github/stars/Ali-Haidar-Sy/Telegram-Anonymous-Chat-Bot-V1?style=for-the-badge&color=yellow"></a>
  <a href="https://github.com/Ali-Haidar-Sy/Telegram-Anonymous-Chat-Bot-V1/blob/main/LICENSE"><img src="https://img.shields.io/github/license/Ali-Haidar-Sy/Telegram-Anonymous-Chat-Bot-V1?style=for-the-badge&color=blue"></a>
  <a href="https://www.python.org/"><img src="https://img.shields.io/badge/Python-3.9+-3776AB?style=for-the-badge&logo=python&logoColor=white"></a>
  <a href="https://pypi.org/project/pyTelegramBotAPI/"><img src="https://img.shields.io/badge/pyTelegramBotAPI-latest-26A5E4?style=for-the-badge&logo=telegram"></a>
  <a href="https://t.me/P33_9"><img src="https://img.shields.io/badge/Telegram-@P33_9-2CA5E0?style=for-the-badge&logo=telegram"></a>
  <a href="https://www.instagram.com/_ungn"><img src="https://img.shields.io/badge/Instagram-@_ungn-E4405F?style=for-the-badge&logo=instagram"></a>
  <a href="https://github.com/Ali-Haidar-Sy"><img src="https://img.shields.io/badge/GitHub-Ali--Haidar--Sy-181717?style=for-the-badge&logo=github"></a>
</p>

---

## 📖 Introduction

**Telegram Anonymous Chat Bot V1** is a feature‑rich Telegram bot that pairs strangers anonymously for private chats.  
Users select their own gender and the gender they prefer to talk with, and the bot automatically matches them with a compatible partner – no waiting around, no manual search.

It's built with **Python** and **pyTelegramBotAPI**, using **SQLite** for lightweight, zero‑config storage.  
The code is clean, well‑structured, and perfect for learning how to build real‑time Telegram bots.

> ⚠️ **Important:** This bot is a demonstration project. If you deploy it publicly, you are responsible for user safety and compliance with Telegram's Terms of Service.

---

## ✨ Features

| Category | Description |
|----------|-------------|
| 🧑‍🤝‍🧑 **Smart Matching** | Choose your gender and the gender you want to chat with – the bot matches automatically. |
| 🌐 **Multilingual** | Full support for **Arabic** and **English** (add more languages easily). |
| 🔐 **Admin Panel** | Broadcast messages, ban / unban users, view global statistics. |
| 📝 **Reporting System** | Users can report inappropriate partners during a chat. |
| 📊 **User Statistics** | Track total chats, join date, and your own profile. |
| 💬 **Rich Media** | Send and receive text, photos, videos, stickers, documents, voice notes, and audio. |
| 🚫 **Ban System** | Temporarily or permanently block users from the bot. |
| ⏳ **Waiting Queue** | Friendly notification when you're still waiting for a partner. |
| 🛡️ **Error Recovery** | Automatically ends broken chats and informs the partner. |
| ⚡ **Performance** | Multi‑threaded for background tasks (waiting notifications). |

---

## 🛠️ Tech Stack

| Component | Technology |
|-----------|-------------|
| Language | Python 3.9+ |
| Bot Library | [pyTelegramBotAPI](https://github.com/eternnoir/pyTelegramBotAPI) |
| Database | SQLite (built‑in `sqlite3`) |
| Environment | `python-dotenv` for secure token handling |
| Concurrency | Threading (waiting queue notifications) |

---

## ⚡ Quick Start

### 1. Clone and install dependencies
```bash
git clone https://github.com/Ali-Haidar-Sy/Telegram-Anonymous-Chat-Bot-V1.git
cd Telegram-Anonymous-Chat-Bot-V1
pip install -r requirements.txt
2. Create your .env file
Rename .env.example to .env and fill in your Bot Token (from @BotFather) and your Telegram User ID (the admin).

bash
cp .env.example .env
nano .env
3. Run the bot
bash
python bot.py
The bot will start polling and respond to commands immediately.

📖 Usage
User Commands
Command	Action
/start	Open the main menu
/stop	End the current chat
/next	Leave the current chat and find a new partner
/lang	Change language (Arabic / English)
/report	Report the current chat partner
/stats	Display your personal statistics
/help	Get a detailed help message
Admin Features (only for the admin ID)
Admin Panel button appears in the main menu.

Broadcast – send a message to all bot users.

Ban / Unban – manage users by their Telegram ID.

Global Stats – view total users, active chats, and more.

📸 Screenshots
<p align="center"> <img src="screenshots/1.png" width="30%"> <img src="screenshots/2.png" width="30%"> <img src="screenshots/3.png" width="30%"> <br> <em>Main menu · Gender selection · Chat interface</em> </p>
📦 Project Structure
text
Telegram-Anonymous-Chat-Bot-V1/
├── bot.py                 # Main bot file
├── requirements.txt       # Python dependencies
├── .env.example           # Template for environment variables
├── .gitignore
├── LICENSE
└── README.md
🤝 Contributing
Pull requests are welcome! For major changes, please open an issue first to discuss what you would like to change.

📝 License
This project is licensed under the MIT License – see the LICENSE file for details.

📞 Contact & Social
Platform	Handle
GitHub	Ali-Haidar-Sy
Telegram	@P33_9
Instagram	@_ungn
<p align="center"> <strong>💬 If this bot inspires you, give it a ⭐ on GitHub!</strong> </p> ```
