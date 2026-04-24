# Quick Start Guide

## 1. Install Dependencies
```bash
pip install -r requirements.txt
```

## 2. Get Telegram Bot Token
- Chat with [@BotFather](https://t.me/botfather)
- Create a new bot
- Copy the token

## 3. Create .env File
```env
TELEGRAM_BOT_TOKEN=your_token_here
```

## 4. Set Up Google OAuth (Easy!)
See [OAUTH2_SETUP.md](OAUTH2_SETUP.md) for detailed instructions.

Quick summary:
- Go to Google Cloud Console
- Create OAuth 2.0 Desktop credentials
- Download as JSON
- Rename to `client_secrets.json`
- Place in project root

## 5. Run the Bot
```bash
python bot.py
```

## 6. Start Using
Send `/start` to your bot and follow the instructions!

## 7. Users Connect to Google Drive
- Send `/google` to the bot
- Click the login link
- Authorize the app
- Send the code back
- Done! Google Drive is connected

---

### Bot Commands
- `/start` - Welcome & instructions
- `/google` - Connect Google Drive (OAuth login)
- `/archive` - Create zip (asks for filename)
- `/clear` - Delete all files
- `/help` - Show help

### Workflow
1. Send files to the bot
2. Type `/archive`
3. Enter a filename
4. Get zip in Telegram + Google Drive (if connected)
5. Type `/clear` to clean up

That's it! 🚀

**The big difference:** No more copying folder IDs or uploading credentials.json!

Users just click a link and the bot handles everything automatically. ✨

