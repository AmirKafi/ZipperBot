# 🔐 Google OAuth2 Setup Guide

This is the new and improved way to connect ZipperBot to Google Drive using OAuth2 authentication!

## How It Works

1. **User clicks `/google`** → Bot sends a login link
2. **User clicks the link** → Google login page opens
3. **User authorizes the app** → Gets an authorization code
4. **User sends the code to bot** → Done! Bot stores credentials
5. **Automatic uploads** → All future archives go to Google Drive

No more manual configuration needed! 🎉

---

## Setup Steps

### Step 1: Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Click on the project dropdown at the top
3. Click "NEW PROJECT"
4. Enter project name: `ZipperBot`
5. Click "CREATE"
6. Wait for the project to be created

### Step 2: Enable Google Drive API

1. In Google Cloud Console, go to "APIs & Services" > "Library"
2. Search for "Google Drive API"
3. Click on "Google Drive API"
4. Click the "ENABLE" button
5. Wait for it to be enabled

### Step 3: Create OAuth 2.0 Credentials

1. Go to "APIs & Services" > "Credentials"
2. Click "CREATE CREDENTIALS" at the top
3. Select "OAuth client ID"
4. If prompted to create a consent screen:
   - Click "CONFIGURE CONSENT SCREEN"
   - Select "External"
   - Click "CREATE"
   - Fill in the form:
     - App name: `ZipperBot`
     - User support email: Your email
     - Leave developer contact empty
     - Click "SAVE AND CONTINUE"
   - Skip scopes (just click "SAVE AND CONTINUE")
   - Skip test users (just click "SAVE AND CONTINUE")
5. Back to credentials, click "CREATE CREDENTIALS" > "OAuth client ID"
6. Choose "Desktop application"
7. Give it a name: `ZipperBot Desktop`
8. Click "CREATE"

### Step 4: Download Credentials

1. After creating the credential, click the download icon (⬇️)
2. Choose "JSON"
3. The file will download as `client_secret_XXXXXX.json`
4. Rename it to `client_secrets.json`
5. Place it in your ZipperBot project root folder

Your file structure should look like:
```
ZipperBot/
├── bot.py
├── client_secrets.json          ← The downloaded file
├── .env
├── requirements.txt
└── ...
```

### Step 5: Run the Bot

```bash
pip install -r requirements.txt
python bot.py
```

---

## User Flow

Once the bot is running, here's what users experience:

### First Time Connection

```
User: /google
Bot: 🔐 Click the link below...
     [LOGIN LINK]
     After you authorize, send me the code!

User: [Clicks link] → Google login → Authorizes → Gets code
User: [Pastes authorization code]

Bot: ✅ Successfully connected to Google Drive!
     Now when you use /archive, files go to Google Drive
```

### Using Archive with Google Drive

```
User: [Sends files]
User: /archive
Bot: What would you like to name your zip file?
User: my_photos
Bot: Creating zip...
     ✅ Archive sent to Telegram
     ☁️ Uploading to Google Drive...
     ✅ File successfully uploaded to Google Drive!
```

---

## What Happens Behind the Scenes

1. **First Time:**
   - Bot creates a folder "ZipperBot Archives" in user's Google Drive
   - Stores the folder ID locally (user-specific)
   - Uploads zip files to this folder

2. **Subsequent Times:**
   - Bot finds the existing "ZipperBot Archives" folder
   - Uploads zip files directly there

3. **Credentials Storage:**
   - Each user's credentials stored in `google_credentials/user_XXXXX_token.json`
   - Folder IDs stored in `google_credentials/user_XXXXX_folder.json`
   - These files are automatically managed by the bot

---

## File Structure After Setup

```
ZipperBot/
├── bot.py
├── client_secrets.json              ← OAuth credentials (REQUIRED)
├── .env                              ← Bot token
├── requirements.txt
├── google_credentials/              ← Auto-created
│   ├── user_123456_token.json       ← User 1 credentials
│   ├── user_123456_folder.json      ← User 1 folder ID
│   ├── user_789012_token.json       ← User 2 credentials
│   └── user_789012_folder.json      ← User 2 folder ID
├── user_files/                       ← Temporary uploads
│   ├── 123456/
│   │   ├── file1.pdf
│   │   └── photo.jpg
│   └── 789012/
│       └── document.txt
└── ...
```

---

## Troubleshooting

### "Google authentication not configured"
- Make sure `client_secrets.json` is in the project root
- Check the filename is exactly `client_secrets.json`

### "Session expired. Please use /google again"
- This happens if you wait too long between `/google` and sending the code
- Just send `/google` again and follow the steps

### Authorization code not working
- Make sure you copied the ENTIRE authorization code
- Try `/google` again and follow the steps carefully
- Check that you clicked "Allow" in the authorization screen

### Already connected but upload fails
- Delete the credentials file: `google_credentials/user_XXXXX_token.json`
- Send `/google` again to re-authenticate

### Files not appearing in Google Drive
- Check that you authorized the app with the right Google account
- Go to https://myaccount.google.com/permissions to verify the app has access
- The "ZipperBot Archives" folder should be in your My Drive

### Can't find credentials file after download
- Look in your Downloads folder
- Make sure you rename it to exactly `client_secrets.json`
- Place it in the same folder as `bot.py`

---

## Security & Privacy

✅ **What we do:**
- Store credentials locally only
- No credentials sent to us
- No credentials logged
- Standard OAuth2 flow

✅ **What users control:**
- They authorize the app themselves
- They can revoke access anytime
- They can delete their local credentials

❌ **What we don't do:**
- Never share credentials
- Never access files without authorization
- Never upload without user permission

### Revoking Access

Users can revoke bot access anytime:
1. Go to [Google Account Permissions](https://myaccount.google.com/permissions)
2. Find "ZipperBot" in the list
3. Click it and select "Remove access"

---

## Differences from Old Method

| Feature | Old (Service Account) | New (OAuth2) |
|---------|----------------------|------------|
| Setup | Complex | Simple |
| Configuration | credentials.json + folder ID | Just client_secrets.json |
| Per-user folders | No (shared) | Yes (each user gets their own) |
| User experience | Copy folder ID | Click link, send code |
| Maintenance | Manual setup | Automatic |
| Security | Less private | More private |

---

## Advanced Configuration (Optional)

### Change folder name
Edit line in `bot.py`:
```python
'name': 'ZipperBot Archives',  # Change this
```

### Change where credentials are stored
Edit line in `bot.py`:
```python
CREDENTIALS_DIR = 'google_credentials'  # Change this
```

### Add more scopes
Edit line in `bot.py`:
```python
DRIVE_SCOPES = ['https://www.googleapis.com/auth/drive']  # Add more if needed
```

---

## Multiple Bot Instances

If you run multiple bots:
- Each needs its own `client_secrets.json`
- Each needs its own `google_credentials/` folder
- Users can be connected to both bots independently

---

**Next Steps:**

1. ✅ Download `client_secrets.json` from Google Cloud Console
2. ✅ Place it in your ZipperBot project root
3. ✅ Run: `python bot.py`
4. ✅ Test with `/google` command
5. ✅ Share the bot with friends!

Enjoy your simplified setup! 🚀
