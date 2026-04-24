# 🎨 OAuth2 Visual Guide

## User Journey

```
┌─────────────────────────────────────────────────────────────┐
│                    FIRST TIME SETUP                          │
└─────────────────────────────────────────────────────────────┘

User                            Bot                          Google
│                              │                              │
├─ /google ─────────────────> │                              │
│                              ├─ Generate OAuth URL ────────>│
│                              │                              │
│                              │<─ Auth URL with code ────────┤
│                              │                              │
│<─ Click link & authorize ──┤                              │
│                              │                              │
│ [Authorize on Google]        │                              │
│                              │                              │
│ [Get authorization code]     │                              │
│                              │                              │
├─ Send code ───────────────> │                              │
│                              ├─ Exchange code for token ───>│
│                              │                              │
│                              │<─ Credentials ─────────────┤
│                              │                              │
│<─ ✅ Connected! ────────────┤                              │
│                              │                              │


┌─────────────────────────────────────────────────────────────┐
│                   USING THE BOT                              │
└─────────────────────────────────────────────────────────────┘

User                            Bot                       Google Drive
│                              │                              │
├─ Send files ─────────────> │                              │
│                              ├─ Store locally               │
│                              │                              │
├─ /archive ────────────────> │                              │
│                              ├─ Ask for filename            │
│<─ "What name?" ───────────┤                              │
│                              │                              │
├─ my_photos ───────────────> │                              │
│                              ├─ Create zip                  │
│                              ├─ Send to Telegram ─────────>│
│<─ 📦 Zip sent! ────────────┤                              │
│                              │                              │
│                              ├─ Get user's service         │
│                              ├─ Check/create folder ──────>│
│                              │                              │
│                              │<─ Folder ID ────────────────┤
│                              │                              │
│                              ├─ Upload zip ───────────────>│
│                              │                              │
│                              │<─ Upload complete ─────────┤
│<─ ☁️ Uploaded! ────────────┤                              │
│                              │                              │
```

---

## File Flow

```
                    ┌─────────────┐
                    │   User      │
                    └──────┬──────┘
                           │ Send files
                           ▼
              ┌────────────────────────┐
              │   user_files/          │
              │   └── {user_id}/       │
              │       ├── file1.pdf    │
              │       └── photo.jpg    │
              └────────────────────────┘
                           │ /archive
                           ▼
              ┌────────────────────────┐
              │   Create zip           │
              │   "my_archive.zip"     │
              └────────────────────────┘
                      │          │
         ┌────────────┘          └────────────┐
         │                                    │
         ▼                                    ▼
    ┌─────────────┐              ┌──────────────────────┐
    │  Telegram   │              │  google_credentials/ │
    │  "Download" │              │  user_123_token.json │
    └─────────────┘              └──────────────────────┘
                                          │
                                          ▼
                                 ┌──────────────────────┐
                                 │  Google Drive        │
                                 │  ZipperBot Archives/ │
                                 │  ├── my_archive.zip  │
                                 └──────────────────────┘
```

---

## Authentication State Machine

```
        ┌──────────────────────────────────┐
        │   No Credentials                 │
        │  /google Not Used Yet            │
        └────────────┬─────────────────────┘
                     │ /google command
                     ▼
        ┌──────────────────────────────────┐
        │  Awaiting Authorization          │
        │  Bot sent OAuth URL              │
        │  User clicking link...           │
        └────────────┬─────────────────────┘
                     │ User authorizes & gets code
                     ▼
        ┌──────────────────────────────────┐
        │  Code Received                   │
        │  User sends authorization code   │
        │  to bot...                       │
        └────────────┬─────────────────────┘
                     │ /archive command
                     ▼
        ┌──────────────────────────────────┐
        │  ✅ AUTHENTICATED                │
        │  Credentials saved locally       │
        │  Ready to upload to Drive        │
        └────────────┬─────────────────────┘
                     │ (Credentials stored)
                     │ (Token refreshes automatically)
                     │
                     └─ Token expires in 1 hour
                        ↓
                     Auto-refresh ✅
```

---

## Data Storage Layout

```
ZipperBot/
│
├── 🐍 bot.py
├── 🔑 client_secrets.json (OAuth credentials)
├── 📝 .env (TELEGRAM_BOT_TOKEN)
│
├── 📁 user_files/
│   ├── 📁 123456789/ (User 1 - alice)
│   │   ├── 📄 document.pdf
│   │   ├── 🖼️ photo.jpg
│   │   └── 🎥 video.mp4
│   │
│   └── 📁 987654321/ (User 2 - bob)
│       ├── 📄 report.docx
│       └── 📄 data.xlsx
│
└── 📁 google_credentials/ (Auto-created)
    ├── 📄 user_123456789_token.json (alice's token)
    ├── 📄 user_123456789_folder.json (alice's folder ID)
    ├── 📄 user_987654321_token.json (bob's token)
    └── 📄 user_987654321_folder.json (bob's folder ID)
```

---

## Google Drive Structure

```
Google Drive (alice@gmail.com)
│
└── 📁 My Drive/
    ├── 📁 ZipperBot Archives/ (Auto-created by bot)
    │   ├── 📦 vacation_photos.zip (Created 2024-04-20)
    │   ├── 📦 work_backup.zip (Created 2024-04-21)
    │   └── 📦 documents_2024.zip (Created 2024-04-22)
    │
    └── [Other files...]
```

```
Google Drive (bob@gmail.com)
│
└── 📁 My Drive/
    ├── 📁 ZipperBot Archives/ (Auto-created by bot)
    │   ├── 📦 my_backup.zip (Created 2024-04-20)
    │   └── 📦 photos.zip (Created 2024-04-21)
    │
    └── [Other files...]
```

Each user has their own isolated folder! 🔒

---

## Function Call Hierarchy

```
/archive command
    │
    ├─→ archive_start()
    │       │
    │       ├─→ Check if files exist
    │       └─→ Ask for filename
    │
    └─→ receive_filename()
            │
            ├─→ Validate filename
            ├─→ Create zip file
            │   └─→ zipfile.ZipFile()
            │
            ├─→ Send to Telegram ✓
            │   └─→ update.message.reply_document()
            │
            ├─→ Check if user connected
            │   └─→ user_has_google_connected()
            │
            └─→ IF connected:
                    │
                    └─→ upload_to_google_drive()
                            │
                            ├─→ get_google_drive_service()
                            │       │
                            │       ├─→ Load user's token
                            │       ├─→ Refresh if needed
                            │       └─→ Build service
                            │
                            ├─→ get_or_create_zipper_folder()
                            │       │
                            │       ├─→ Check if folder exists
                            │       ├─→ If not, create it
                            │       └─→ Save folder ID
                            │
                            └─→ Upload file
                                    └─→ service.files().create()
```

---

## State Timeline

```
Time    State              Action                    Result
────────────────────────────────────────────────────────────
T0      Not connected      User sends /google        Show OAuth URL
        ↓
T1      Awaiting auth      User clicks link          Google login
        ↓
T2      Awaiting auth      User authorizes app       Get code
        ↓
T3      Awaiting code      User sends code           Verify code
        ↓
T4      ✅ CONNECTED       Save credentials         Success! ✅
        ↓
T5      CONNECTED          User sends files         Files stored
        ↓
T6      CONNECTED          User sends /archive       Ask filename
        ↓
T7      CONNECTED          User sends filename       Validate
        ↓
T8      CONNECTED          Create zip               Zip created
        ↓
T9      CONNECTED          Upload to Telegram       Telegram ✓
        ↓
T10     CONNECTED          Get Drive service        Token refreshed
        ↓
T11     CONNECTED          Create/get folder        Folder ready
        ↓
T12     ✅ COMPLETE        Upload to Drive          Drive ✓ ✅
```

---

## Error Handling Flow

```
                    ┌──────────────────┐
                    │  User Action     │
                    └────────┬─────────┘
                             │
                    ┌────────▼──────────┐
                    │  Try Operation   │
                    └────────┬─────────┘
                             │
                   ┌─────────┴─────────┐
                   │                   │
                ✅ Success         ❌ Error
                   │                   │
                   │        ┌──────────▼─────────┐
                   │        │  Catch Exception  │
                   │        └──────────┬─────────┘
                   │                   │
                   │        ┌──────────▼────────────┐
                   │        │  Send Error Message  │
                   │        │  to User             │
                   │        └──────────┬────────────┘
                   │                   │
                   └────────────┬──────┘
                                │
                        ┌───────▼──────┐
                        │  Bot Ready   │
                        │  for Next    │
                        │  Command     │
                        └──────────────┘
```

---

## Credential Refresh Cycle

```
Initial Token
    │
    ├─ Valid for 1 hour
    ├─ Stored in user_123456_token.json
    │
    ▼
Hour passes...
    │
    ├─ Next request uses token
    ├─ Google: "Token expired"
    │
    ▼
Bot Detects Expiration
    │
    ├─ creds.expired = True
    ├─ creds.refresh_token exists
    │
    ▼
Request New Token
    │
    ├─ creds.refresh(Request())
    ├─ Get new token from Google
    │
    ▼
Save New Token
    │
    ├─ Write to user_123456_token.json
    ├─ User doesn't know it happened! ✅
    │
    ▼
Continue Using
    │
    └─ Seamless for user
```

---

## Compare: OAuth2 vs Old Service Account

```
OAUTH2 (NEW)                    SERVICE ACCOUNT (OLD)
─────────────────────────────────────────────────────

┌─────────────────────┐        ┌──────────────────────┐
│ User Setup          │        │ Admin Setup          │
├─────────────────────┤        ├──────────────────────┤
│ 1. Click link       │        │ 1. Create project    │
│ 2. Login            │        │ 2. Create account    │
│ 3. Authorize        │        │ 3. Download JSON     │
│ 4. Send code        │        │ 4. Create folder     │
│ 5. Done!            │        │ 5. Share folder      │
│                     │        │ 6. Copy folder ID    │
│ ✅ 5 steps, user   │        │ 7. Add to .env       │
│ ✅ Simple          │        │                      │
│ ✅ Clear           │        │ ❌ 7 steps, complex │
│                     │        │ ❌ Error-prone      │
└─────────────────────┘        └──────────────────────┘

┌─────────────────────┐        ┌──────────────────────┐
│ Security            │        │ Security             │
├─────────────────────┤        ├──────────────────────┤
│ ✅ Per-user token  │        │ ⚠️ Shared token     │
│ ✅ User owns data   │        │ ⚠️ Admin owns data   │
│ ✅ Auto refresh     │        │ ❌ Manual refresh    │
│ ✅ Can revoke       │        │ ⚠️ Hard to revoke   │
└─────────────────────┘        └──────────────────────┘

┌─────────────────────┐        ┌──────────────────────┐
│ Folders             │        │ Folders              │
├─────────────────────┤        ├──────────────────────┤
│ ✅ Each user owns   │        │ ❌ Shared by all     │
│ ✅ Auto created     │        │ ❌ Manual creation   │
│ ✅ Isolated data    │        │ ❌ Mixed files       │
└─────────────────────┘        └──────────────────────┘
```

---

This visual guide should help you understand how the OAuth2 system works! 🎨

For detailed technical info, see [OAUTH2_IMPLEMENTATION.md](OAUTH2_IMPLEMENTATION.md)
