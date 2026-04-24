# 🔄 OAuth2 Upgrade - What Changed

## The Big Improvement ✨

Instead of service accounts and manual folder setup, ZipperBot now uses **OAuth2 authentication** - just like regular Google apps!

---

## Before vs After

### Before (Service Account) ❌
```
Setup Steps:
1. Create service account
2. Download credentials.json
3. Get service account email
4. Create folder in Google Drive
5. Share folder with service account
6. Copy folder ID
7. Add folder ID to .env file
8. Repeat for each admin user

Issues:
- Complex setup
- All users share same folder
- Manual configuration
- Error-prone
- Not user-friendly
```

### After (OAuth2) ✅
```
Setup Steps:
1. Create OAuth 2.0 credentials
2. Download client_secrets.json
3. Place in bot folder
4. Done!

User Experience:
1. User sends /google
2. User clicks login link
3. User authorizes
4. User sends code
5. Done! Google connected

Benefits:
- Simple setup
- Each user has own folder
- Automatic folder creation
- User-friendly
- More secure
```

---

## Technical Changes

### Code Changes

**Old Approach:**
```python
from google.oauth2 import service_account
from googleapiclient.discovery import build as drive_build

# Loaded service account credentials from file
creds = service_account.Credentials.from_service_account_file(
    'credentials.json', scopes=SCOPES)
service = drive_build('drive', 'v3', credentials=creds)

# Uploaded to single shared folder
file = service.files().create(
    body={'name': filename, 'parents': [GOOGLE_DRIVE_FOLDER_ID]},
    ...
)
```

**New Approach:**
```python
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials

# User authenticates via OAuth2 flow
flow = InstalledAppFlow.from_client_secrets_file('client_secrets.json', DRIVE_SCOPES)
creds = flow.run_local_server()

# Bot creates folder automatically
folder = service.files().create(
    body={'name': 'ZipperBot Archives', 'mimeType': 'application/vnd.google-apps.folder'},
    fields='id'
).execute()

# Uploaded to user's own folder
file = service.files().create(
    body={'name': filename, 'parents': [user_folder_id]},
    ...
)
```

### New Functions

Added to support OAuth2:
- `ensure_credentials_dir()` - Create credentials storage folder
- `get_user_credentials_path()` - Get path to user's credentials
- `get_user_drive_folder_path()` - Get path to user's folder ID
- `get_google_drive_service(user_id)` - Get service for specific user
- `get_or_create_zipper_folder()` - Auto-create user's archive folder
- `google_login()` - Handle `/google` command
- `handle_google_code()` - Handle authorization code
- `user_has_google_connected()` - Check if user is authenticated

### Modified Functions

- `upload_to_google_drive()` - Now takes `user_id` parameter
- `receive_filename()` - Uses new upload function
- `start()` - Shows Google connection status
- `main()` - Added Google handlers

### New Command

- `/google` - Start OAuth2 authentication flow

---

## File Structure Changes

### Before
```
ZipperBot/
├── bot.py
├── credentials.json              ← Service account (sensitive!)
├── .env                          ← Had GOOGLE_DRIVE_FOLDER_ID
└── user_files/
```

### After
```
ZipperBot/
├── bot.py
├── client_secrets.json           ← OAuth credentials (safer)
├── .env                          ← Just bot token now
├── google_credentials/           ← Auto-created
│   ├── user_123456_token.json   ← Per-user credentials
│   └── user_123456_folder.json  ← Per-user folder ID
└── user_files/
```

---

## User Experience Flow

### Authentication

```
User: /google
  ↓
Bot: [Shows login link]
  ↓
User: [Clicks link, logs in, authorizes]
  ↓
User: [Copies authorization code]
  ↓
User: [Sends code to bot]
  ↓
Bot: ✅ Connected!
```

### Archiving

```
User: [Sends files] → [/archive] → [Types filename]
  ↓
Bot: Creates zip
  ↓
Bot: Sends to Telegram ✓
  ↓
Bot: Creates "ZipperBot Archives" folder (if first time)
  ↓
Bot: Uploads to Google Drive ✓
  ↓
User: Gets notifications of success
```

---

## Benefits

### For Bot Operators
- ✅ Simpler setup (no folder IDs to copy)
- ✅ Cleaner configuration (.env has less)
- ✅ More scalable (easy for multiple users)
- ✅ Better security (per-user isolation)

### For End Users
- ✅ Intuitive authentication (like Gmail login)
- ✅ Own folder in Google Drive
- ✅ No manual configuration needed
- ✅ Can revoke access anytime

### For Security
- ✅ No shared service account credentials
- ✅ User-specific OAuth tokens
- ✅ Standard OAuth2 flow
- ✅ Credentials stored locally, never shared

---

## Migration Guide

If you had the old version and want to upgrade:

### Step 1: Backup (Optional)
```bash
# Backup your old .env if you want
cp .env .env.backup
```

### Step 2: Update Code
```bash
git pull  # Or download the new files
```

### Step 3: Update Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Remove Old Files
```bash
# Remove old service account credentials
rm credentials.json  # If you had one
```

### Step 5: Create New .env
```env
TELEGRAM_BOT_TOKEN=your_token_here
# That's it! No GOOGLE_DRIVE_FOLDER_ID needed
```

### Step 6: Get OAuth Credentials
Follow [OAUTH2_SETUP.md](OAUTH2_SETUP.md) to:
1. Create OAuth 2.0 credentials in Google Cloud Console
2. Download as JSON
3. Save as `client_secrets.json` in bot folder

### Step 7: Restart Bot
```bash
python bot.py
```

### Step 8: Old Users Need to Reconnect
- They should send `/google` to re-authenticate
- They'll get their own folder automatically
- Everything works as before, but better!

---

## Backward Compatibility

❌ **Not backward compatible** with old version

Old users:
- Will need to send `/google` to authenticate
- Will get a new folder automatically
- Old uploads won't be affected (still in old shared folder)

---

## Dependencies Update

### Removed
- (None - we just changed which imports we use)

### Added
- `InstalledAppFlow` from `google_auth_oauthlib.flow`
- `Credentials` from `google.oauth2.credentials`
- `Request` from `google.auth.transport.requests`

### Still Required
```
python-telegram-bot==20.5
python-dotenv==1.0.0
google-auth-oauthlib==1.2.0
google-auth-httplib2==0.2.0
google-api-python-client==2.100.0
google-auth==2.28.0
```

---

## What Stayed the Same

✅ Telegram integration (unchanged)
✅ File handling (unchanged)
✅ Archive creation (unchanged)
✅ Filename validation (unchanged)
✅ `/archive` command (unchanged)
✅ `/clear` command (unchanged)
✅ `/start` command (unchanged)
✅ `/help` command (unchanged)

---

## Summary

This upgrade makes ZipperBot:
- 🎯 **Easier** to set up
- 👥 **More personal** (each user has their own folder)
- 🔒 **More secure** (per-user OAuth tokens)
- 😊 **More user-friendly** (just click a link)

All the core functionality stays the same, but the Google Drive experience is massively improved! 🚀

---

**Questions?** Check [OAUTH2_SETUP.md](OAUTH2_SETUP.md) for detailed instructions.
