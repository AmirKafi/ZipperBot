# Code Structure & Documentation

## bot.py - Main Application File

### Imports Section
```python
# Core libraries
import os, zipfile, tempfile, shutil, io
from pathlib import Path

# Telegram
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler

# Google Drive
from google.oauth2 import service_account
from googleapiclient.discovery import build as drive_build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload

# Configuration
from dotenv import load_dotenv
```

### Global Configuration
```python
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
GOOGLE_DRIVE_FOLDER_ID = os.getenv('GOOGLE_DRIVE_FOLDER_ID')
GOOGLE_CREDENTIALS_FILE = 'credentials.json'
TEMP_DIR = 'user_files'
AWAITING_FILENAME = 1  # Conversation state
```

---

## Function Reference

### Authentication Functions

#### `get_google_drive_service()`
- **Purpose:** Initialize and authenticate with Google Drive API
- **Parameters:** None
- **Returns:** Google Drive service object or None
- **Error Handling:** Returns None if credentials missing
- **Used By:** `upload_to_google_drive()`

#### `upload_to_google_drive(zip_path, filename, service)`
- **Purpose:** Upload zip file to Google Drive
- **Parameters:**
  - `zip_path`: Path to the zip file
  - `filename`: Name for the file (without .zip)
  - `service`: Google Drive service object
- **Returns:** Boolean (True if successful)
- **Errors Handled:** HttpError, general exceptions

---

### Bot Command Handlers

#### `start(update, context)`
- **Trigger:** `/start` command
- **Purpose:** Send welcome message
- **Features:**
  - Shows bot capabilities
  - Lists available commands
  - Emoji-rich formatting

#### `help_command(update, context)`
- **Trigger:** `/help` command
- **Purpose:** Display detailed help information
- **Features:**
  - Feature overview
  - Command reference
  - Usage examples

#### `archive_start(update, context)` ⭐ **NEW**
- **Trigger:** `/archive` command (start)
- **Purpose:** Initiate archive process
- **Returns:** `AWAITING_FILENAME` state
- **Features:**
  - Validates user has files
  - Stores user_id in context
  - Asks for filename
  - Returns conversation state

#### `receive_filename(update, context)` ⭐ **NEW**
- **Trigger:** User input during archive
- **Purpose:** Receive filename and create archive
- **Features:**
  - Validates filename (no invalid characters)
  - Checks length (1-50 characters)
  - Creates zip with custom name
  - Uploads to Telegram
  - Uploads to Google Drive (if configured)
  - Shows file size
  - Cleans up temporary files
- **Returns:** `ConversationHandler.END`

#### `cancel_archive(update, context)` ⭐ **NEW**
- **Trigger:** `/cancel` command
- **Purpose:** Cancel current archive operation
- **Returns:** `ConversationHandler.END`

#### `clear_files(update, context)`
- **Trigger:** `/clear` command
- **Purpose:** Delete all user files
- **Features:**
  - Removes entire user folder
  - Confirmation message

---

### File Handling

#### `handle_file(update, context)`
- **Trigger:** File upload (document, photo, video, audio, voice)
- **Purpose:** Download and store user files
- **Features:**
  - Detects file type
  - Creates user-specific folder
  - Downloads file from Telegram
  - Generates appropriate filename
  - Shows file count
- **Supported Types:**
  - Document (file_name preserved)
  - Photo (auto-named as photo_N.jpg)
  - Video (auto-named as video_*.mp4)
  - Audio (auto-named as audio_*.mp3)
  - Voice (auto-named as voice_*.ogg)

---

### Application Setup

#### `main()`
- **Purpose:** Initialize and start the bot
- **Setup Steps:**
  1. Validates TELEGRAM_BOT_TOKEN
  2. Creates Application instance
  3. Sets up ConversationHandler for archive flow
  4. Registers all command handlers
  5. Registers file handlers
  6. Starts polling

---

## Conversation Flow (Archive Process)

```
User sends /archive
        ↓
archive_start() checks for files
        ↓
Bot asks: "What filename?"
        ↓
User types filename
        ↓
receive_filename() validates
        ↓
Filename valid? 
    ├─ NO  → Show error, ask again
    └─ YES → Continue
        ↓
Create zip file
        ↓
Send zip to Telegram
        ↓
Upload to Google Drive (if configured)
        ↓
Show success message
        ↓
ConversationHandler.END
```

---

## File Storage Structure

```
user_files/
└── {user_id}/           # Unique per user
    ├── document.pdf
    ├── photo_0.jpg
    ├── photo_1.jpg
    ├── video_abc123.mp4
    └── voice_def456.ogg

# Zip files created temporarily:
archive_filename.zip     # Created in TEMP_DIR
# Then deleted after upload
```

---

## Error Handling

### Bot Level
- Missing TELEGRAM_BOT_TOKEN → Print error and exit
- File download fails → Send error message to user
- Zip creation fails → Send error message to user

### Google Drive Level
- Missing credentials.json → Show warning, continue without Drive
- Missing GOOGLE_DRIVE_FOLDER_ID → Skip upload, show info message
- API errors → Catch and report to user

### File Level
- Invalid filename characters → Ask user to try again
- Filename too long/short → Validation + retry
- No files to archive → Clear error message

---

## Dependencies & Versions

```
python-telegram-bot==20.5      # Telegram bot API
python-dotenv==1.0.0           # Environment variables
google-auth-oauthlib==1.2.0   # Google OAuth
google-auth-httplib2==0.2.0   # HTTP adapter
google-api-python-client==2.100.0  # Google Drive API
```

---

## Configuration Variables

| Variable | Type | Required | Default | Used In |
|----------|------|----------|---------|---------|
| TELEGRAM_BOT_TOKEN | str | Yes | - | main(), bot auth |
| GOOGLE_DRIVE_FOLDER_ID | str | No | None | upload_to_google_drive() |
| GOOGLE_CREDENTIALS_FILE | str | No | credentials.json | get_google_drive_service() |
| TEMP_DIR | str | No | user_files | All file operations |
| AWAITING_FILENAME | int | - | 1 | ConversationHandler state |

---

## Key Design Decisions

1. **Per-User Storage** - Each user has isolated folder (privacy)
2. **Temporary Files** - Zip files deleted after upload (disk space)
3. **Service Account** - Used for Google Drive (no user auth needed)
4. **Conversation Handler** - Better UX than command-only approach
5. **Filename Validation** - Prevents filesystem errors
6. **Graceful Degradation** - Works without Google Drive

---

## Extensibility

### Adding New File Types
Edit `handle_file()` to add new file types (currently supports Document, Photo, Video, Audio, Voice)

### Adding New Commands
1. Create async handler function
2. Register with `application.add_handler(CommandHandler("cmd", handler))`

### Modifying Compression
Edit `zipfile.ZipFile()` to change compression level (ZIP_DEFLATED is current)

### Custom Storage
Change `TEMP_DIR` variable and path handling logic

---

## Testing Checklist

- [ ] Bot starts without errors
- [ ] `/start` displays welcome message
- [ ] Can send and receive documents
- [ ] Can send and receive photos
- [ ] Can send and receive videos
- [ ] `/archive` asks for filename
- [ ] Filename validation works
- [ ] Zip file created successfully
- [ ] Zip file received in Telegram
- [ ] File size displayed correctly
- [ ] Google Drive upload works (if configured)
- [ ] `/clear` deletes files
- [ ] `/help` shows help message
- [ ] `/cancel` stops archive process
- [ ] Error messages display properly

---

**For more information, see:**
- [README.md](README.md) - Full documentation
- [QUICK_START.md](QUICK_START.md) - Quick setup
- [GOOGLE_DRIVE_SETUP.md](GOOGLE_DRIVE_SETUP.md) - Drive integration
- [CONFIGURATION.md](CONFIGURATION.md) - Configuration reference
