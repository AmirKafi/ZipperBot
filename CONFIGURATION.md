# Configuration Reference

## Environment Variables (.env)

Create a `.env` file in the project root with the following variables:

### Required

```env
TELEGRAM_BOT_TOKEN=your_bot_token_here
```

**How to get it:**
1. Go to Telegram and find [@BotFather](https://t.me/botfather)
2. Type `/start` and follow the prompts to create a new bot
3. Copy the token provided
4. Paste it in the `.env` file

**Format:** `123456789:ABCdef-GHIjklMNOp_QrsTUvWxyz`

---

### Optional

```env
GOOGLE_DRIVE_FOLDER_ID=your_folder_id_here
```

**What it is:** The ID of the Google Drive folder where zip files will be uploaded

**How to get it:**
1. Create a folder in Google Drive
2. Open the folder
3. Look at the URL: `https://drive.google.com/drive/folders/ABC123XYZ456`
4. Copy the part after `/folders/` (ABC123XYZ456)
5. Paste it in the `.env` file

**If not set:** Google Drive uploads will be skipped (bot still works fine)

---

## .env Template

Copy this template to create your `.env` file:

```env
# Telegram Bot Configuration (REQUIRED)
TELEGRAM_BOT_TOKEN=your_bot_token_here

# Google Drive Configuration (OPTIONAL)
# Leave empty if you don't want Google Drive integration
GOOGLE_DRIVE_FOLDER_ID=your_folder_id_here
```

---

## credentials.json (For Google Drive)

**Location:** Project root directory (same level as bot.py)

**Purpose:** Contains Google service account credentials

**How to create it:**
1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create a new project
3. Enable Google Drive API
4. Create a Service Account
5. Create and download a JSON key
6. Save as `credentials.json` in your project

**Format:** JSON file (don't modify the contents)

**Security:** Add to .gitignore (already done)

---

## File Locations Reference

```
h:\Projects\Back-End & MVC\ZipperBot\
│
├── .env                      ← Your configuration (create this)
│   └── TELEGRAM_BOT_TOKEN=...
│   └── GOOGLE_DRIVE_FOLDER_ID=...
│
├── credentials.json          ← Google credentials (create if using Drive)
│
├── bot.py                    ← Main bot file
│
├── user_files/               ← Auto-created for temporary storage
│   └── {user_id}/
│       ├── file1.pdf
│       ├── photo.jpg
│       └── ...
│
└── [Documentation files]
    ├── README.md
    ├── QUICK_START.md
    ├── GOOGLE_DRIVE_SETUP.md
    └── FEATURES_SUMMARY.md
```

---

## Minimal Configuration

**To get started with just Telegram (no Google Drive):**

1. Create `.env` file
2. Add only: `TELEGRAM_BOT_TOKEN=your_token`
3. Run: `python bot.py`

That's it! The bot will work perfectly without Google Drive.

---

## Full Configuration

**To use all features (Telegram + Google Drive):**

1. Create `.env` with both variables
2. Add `credentials.json` to project root
3. Share Google Drive folder with service account
4. Run: `python bot.py`

---

## Troubleshooting Configuration

### Bot won't start - "TELEGRAM_BOT_TOKEN not found"
- Check .env file exists in project root
- Check variable name is exactly: `TELEGRAM_BOT_TOKEN`
- Check token value is not empty
- Check no typos in the token

### Google Drive uploads fail - "credentials.json not found"
- Check credentials.json exists in project root
- Check filename is exactly: `credentials.json`
- Check file is not corrupted
- Re-download from Google Cloud Console if needed

### Google Drive uploads fail - folder ID issues
- Check GOOGLE_DRIVE_FOLDER_ID is copied correctly
- Check folder is shared with service account email
- Check service account has "Editor" access
- Verify folder ID from URL (after /folders/)

### Files aren't saved
- Check `user_files/` directory exists
- Check disk space available
- Check file permissions on user_files/ folder
- Check antivirus isn't blocking file writes

---

## Best Practices

✅ **Do's:**
- Keep .env in project root
- Keep credentials.json secret (in .gitignore)
- Use strong folder permissions
- Backup your .env file
- Test with /start command first

❌ **Don'ts:**
- Don't share credentials.json
- Don't commit .env to git
- Don't modify credentials.json content
- Don't use bot token in public code
- Don't grant unnecessary permissions

---

## Example .env File

Here's what a complete .env file looks like:

```env
# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN=1234567890:ABCdef-GHIjklMNOp_QrsTUvWxyz1234567

# Google Drive Configuration  
GOOGLE_DRIVE_FOLDER_ID=1aBC2dEfGhIjKlMnOpQrStUvWxYz3456789
```

---

## Environment Variables in Code

The bot reads these variables in [bot.py](bot.py):

```python
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
GOOGLE_DRIVE_FOLDER_ID = os.getenv('GOOGLE_DRIVE_FOLDER_ID')
GOOGLE_CREDENTIALS_FILE = 'credentials.json'
```

No need to modify the code - just set the variables in .env!

---

**Need help?** Check [QUICK_START.md](QUICK_START.md) or [README.md](README.md)
