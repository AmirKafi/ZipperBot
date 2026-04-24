# ZipperBot 📦

A Telegram bot that archives files and creates downloadable zip files with easy Google Drive integration using OAuth2!

## Features

✨ **Easy File Archiving**
- Send any files to the bot (documents, photos, videos, audio)
- Automatically saves all files
- Creates zip archives on demand

📤 **Direct Telegram Upload**
- Download zip files directly in Telegram
- No external links or complicated setup
- File compression for smaller downloads

☁️ **One-Click Google Drive Integration**
- Users just click a link and authorize
- Bot automatically creates a "ZipperBot Archives" folder
- All zip files go to their Google Drive
- No manual folder setup needed!

📝 **Custom Filenames**
- Choose meaningful names for your archives
- Easy organization and identification

🔒 **User Privacy**
- Files stored separately per user
- Each user has their own Google Drive folder
- Easy cleanup with `/clear` command
- No shared credentials needed

## Quick Setup

### Prerequisites
- Python 3.8+
- A Telegram bot token from [@BotFather](https://t.me/botfather)
- Google OAuth credentials (easy 5-minute setup)

### Installation

1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Create `.env` file**
   ```env
   TELEGRAM_BOT_TOKEN=your_token_here
   ```

3. **Set up Google OAuth** (see [OAUTH2_SETUP.md](OAUTH2_SETUP.md))
   - Create OAuth 2.0 credentials in Google Cloud Console
   - Download as JSON
   - Save as `client_secrets.json` in project root

4. **Run the bot**
   ```bash
   python bot.py
   ```

Done! 🎉

## Usage

### For Bot Owner/Operator
1. Get Telegram bot token
2. Download Google OAuth credentials
3. Run `python bot.py`
4. Give bot link to users

### For End Users
1. Send `/start` to see options
2. Send `/google` to connect Google Drive (one-time setup)
3. Send files to the bot
4. Send `/archive` to create zip
5. Choose a filename
6. Get zip in Telegram + Google Drive automatically!

## Commands

| Command | Description |
|---------|-------------|
| `/start` | Show welcome message and instructions |
| `/archive` | Create zip file from all your files |
| `/google` | Connect your Google Drive account (OAuth login) |
| `/clear` | Delete all your files and start fresh |
| `/help` | Show detailed help information |

## How OAuth2 Works

**Simple 3-Step Process:**

```
1. User sends /google
   ↓
2. Bot sends login link → User clicks → Authorizes → Gets code
   ↓
3. User sends code to bot → Bot stores credentials → Done!
```

That's it! No more copying folder IDs or uploading credentials files. ✨

---

## File Types Supported

- 📄 Documents (PDF, Word, Excel, etc.)
- 📸 Photos
- 🎥 Videos
- 🎵 Audio files
- 🎤 Voice messages

## Storage

Files are stored in the `user_files/` directory organized by user ID:
```
user_files/
├── 123456789/
│   ├── document.pdf
│   ├── photo.jpg
│   └── ...
└── 987654321/
    └── ...
```

Google credentials stored locally in `google_credentials/`:
```
google_credentials/
├── user_123456789_token.json      # User's Google credentials
├── user_123456789_folder.json     # User's Drive folder ID
├── user_987654321_token.json
└── user_987654321_folder.json
```

Zip files are created temporarily and cleaned up after sending.

## Configuration

### Environment Variables (.env)

```env
# Required
TELEGRAM_BOT_TOKEN=your_bot_token_here

# Optional - for advanced users
# Usually not needed, defaults are fine
```

### OAuth Credentials (client_secrets.json)

- Download from Google Cloud Console
- Place in project root
- This is how users authenticate securely

---

## Troubleshooting

### Bot not responding
- Check that `TELEGRAM_BOT_TOKEN` is correct in `.env`
- Ensure you've sent `/start` to the bot first
- Check internet connection

### Google authentication not working
- Make sure `client_secrets.json` is in project root (same folder as bot.py)
- Verify Google Drive API is enabled in Google Cloud Console
- Try `/google` again

### Authorization code not working
- Make sure you copied the entire code
- Try `/google` again
- Check that you clicked "Allow" on the Google consent screen

### Files not uploading to Google Drive
- Verify you sent `/google` and completed authorization
- Check that you authorized with the correct Google account
- Try `/google` again to re-authenticate

### Zip creation fails
- Check disk space available
- Verify all files in user folder are accessible
- Try `/clear` and upload files again

---

## Advanced Configuration

You can modify the following in `bot.py`:
- `TEMP_DIR` - Change where files are stored
- `CREDENTIALS_DIR` - Change where Google credentials are stored
- `DRIVE_SCOPES` - Change API permissions (advanced users only)

---

## Requirements

See `requirements.txt` for all dependencies:
- `python-telegram-bot` - Telegram bot API wrapper
- `python-dotenv` - Environment variable management
- `google-auth-oauthlib` - Google OAuth authentication
- `google-auth-httplib2` - Google HTTP library
- `google-api-python-client` - Google Drive API client
- `google-auth` - Google authentication library

---

## Project Structure

```
ZipperBot/
├── bot.py                      # Main application
├── requirements.txt            # Dependencies
├── client_secrets.json         # Google OAuth (after setup)
├── .env                        # Bot token
├── README.md                   # This file
├── QUICK_START.md             # Quick setup guide
├── OAUTH2_SETUP.md            # Detailed OAuth setup
├── FEATURES_SUMMARY.md        # Feature overview
├── CODE_STRUCTURE.md          # Code documentation
├── .gitignore                 # Git ignore rules
├── google_credentials/        # User credentials (auto-created)
└── user_files/                # Temporary storage (auto-created)
```

---

## Security & Privacy

✅ **What we protect:**
- User credentials stored locally
- Each user has isolated storage
- Google credentials never logged
- Standard OAuth2 flow

✅ **User control:**
- Users authenticate themselves
- Users can revoke access anytime via Google Account
- Users can delete local files anytime

---

## License

This project is open source and available for personal use.

## Support

For detailed information:
1. Check [QUICK_START.md](QUICK_START.md) for quick setup
2. See [OAUTH2_SETUP.md](OAUTH2_SETUP.md) for OAuth2 guide
3. Read [CODE_STRUCTURE.md](CODE_STRUCTURE.md) for code details
4. Check [FEATURES_SUMMARY.md](FEATURES_SUMMARY.md) for feature overview

---

Made with ❤️ for easy file archiving on Telegram
