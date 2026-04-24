# 🔧 OAuth2 Implementation Details

This document explains exactly how the OAuth2 implementation works.

---

## Authentication Flow

### User-First Design

```
User clicks /google command
    ↓
Bot generates OAuth URL
    ↓
Bot sends URL to user
    ↓
User clicks link → Google login page opens
    ↓
User sees "ZipperBot wants to access your Google Drive"
    ↓
User clicks "Allow"
    ↓
Google shows authorization code
    ↓
User copies code and sends to bot
    ↓
Bot exchanges code for credentials
    ↓
Bot stores credentials locally
    ↓
User is authenticated! ✅
```

---

## How It Works Technically

### Step 1: User Sends /google

```python
async def google_login(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # 1. Check if client_secrets.json exists
    if not os.path.exists('client_secrets.json'):
        # Show error if not configured
        return
    
    # 2. Create OAuth flow
    flow = InstalledAppFlow.from_client_secrets_file(
        'client_secrets.json',
        scopes=DRIVE_SCOPES
    )
    
    # 3. Generate authorization URL
    auth_url, _ = flow.authorization_url(prompt='consent')
    
    # 4. Store flow in context for later use
    context.user_data['google_flow'] = flow
    context.user_data['google_user_id'] = user_id
    
    # 5. Send URL to user
    await update.message.reply_text(f"Click here: {auth_url}")
```

### Step 2: User Gets Code from Google

Google redirects user to localhost with code:
```
http://localhost:8080/?code=AUTHORIZATION_CODE&state=...
```

User sees the code and copies it.

### Step 3: User Sends Code to Bot

```python
async def handle_google_code(update: Update, context: ContextTypes.DEFAULT_TYPE):
    auth_code = update.message.text.strip()
    
    # 1. Get the flow we stored earlier
    flow = context.user_data.get('google_flow')
    
    # 2. Exchange authorization code for credentials
    flow.fetch_token(code=auth_code)
    creds = flow.credentials
    
    # 3. Save credentials to user's credential file
    creds_path = get_user_credentials_path(user_id)
    with open(creds_path, 'w') as token:
        token.write(creds.to_json())
    
    # 4. Confirm success
    await update.message.reply_text("✅ Connected!")
```

### Step 4: Archive Uploads to Google Drive

```python
async def receive_filename(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    
    # 1. Check if user is authenticated
    if user_has_google_connected(user_id):
        # 2. Upload the zip
        if upload_to_google_drive(user_id, zip_path, filename):
            await update.message.reply_text("✅ Uploaded to Google Drive!")
        else:
            await update.message.reply_text("❌ Upload failed")
    else:
        await update.message.reply_text("Use /google first")
```

---

## Data Storage

### Credential Files

```
google_credentials/
├── user_123456789_token.json      # User's OAuth token
└── user_123456789_folder.json     # User's folder ID
```

### User Token JSON Structure

```json
{
  "token": "ya29.a0AfH6SMB...",
  "refresh_token": "1//0gLF0F...",
  "token_uri": "https://oauth2.googleapis.com/token",
  "client_id": "123456789-abcdef.apps.googleusercontent.com",
  "client_secret": "GOCSPX-abc123...",
  "scopes": ["https://www.googleapis.com/auth/drive"],
  "type": "authorized_user"
}
```

### Folder Info JSON Structure

```json
{
  "folder_id": "1a2b3c4d5e6f7g8h9i0j1k2l"
}
```

---

## Google Drive Folder Creation

### Automatic Folder Creation Process

```python
def get_or_create_zipper_folder(user_id: int, service) -> str:
    folder_info_path = get_user_drive_folder_path(user_id)
    
    # 1. Check if we already have a folder ID
    if os.path.exists(folder_info_path):
        with open(folder_info_path, 'r') as f:
            folder_info = json.load(f)
            folder_id = folder_info.get('folder_id')
            
            # 2. Verify folder still exists
            try:
                service.files().get(fileId=folder_id).execute()
                return folder_id  # Folder exists, use it
            except:
                pass  # Folder deleted, create new one
    
    # 3. Create new folder
    file_metadata = {
        'name': 'ZipperBot Archives',
        'mimeType': 'application/vnd.google-apps.folder'
    }
    
    folder = service.files().create(
        body=file_metadata, 
        fields='id'
    ).execute()
    
    folder_id = folder.get('id')
    
    # 4. Save folder ID for future use
    folder_info = {'folder_id': folder_id}
    with open(folder_info_path, 'w') as f:
        json.dump(folder_info, f)
    
    return folder_id
```

---

## Credentials Management

### Getting User Service

```python
def get_google_drive_service(user_id: int):
    creds_path = get_user_credentials_path(user_id)
    
    # 1. Check if credentials file exists
    if os.path.exists(creds_path):
        # 2. Load credentials from file
        creds = Credentials.from_authorized_user_file(creds_path, DRIVE_SCOPES)
        
        # 3. Refresh if needed (tokens expire after 1 hour)
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            
            # 4. Save refreshed credentials
            with open(creds_path, 'w') as token:
                token.write(creds.to_json())
        
        # 5. Build and return service
        return build('drive', 'v3', credentials=creds)
    
    return None
```

### Token Refresh Mechanism

```
Token obtained ──→ User uses bot ──→ Token expires (1 hour later)
    ↓                                        ↓
Auto-refresh triggered when needed ←── Request to Google
    ↓
New token saved to user's credential file
    ↓
Next request uses new token
```

---

## Upload Process

### Uploading Zip to Google Drive

```python
def upload_to_google_drive(user_id: int, zip_path: str, filename: str) -> bool:
    # 1. Get authenticated service for user
    service = get_user_drive_service(user_id)
    
    # 2. Get or create user's folder
    folder_id = get_or_create_zipper_folder(user_id, service)
    
    # 3. Prepare file metadata
    file_metadata = {
        'name': f"{filename}.zip",
        'parents': [folder_id]  # Put in user's folder
    }
    
    # 4. Prepare file for upload
    media = MediaFileUpload(zip_path, mimetype='application/zip')
    
    # 5. Upload to Google Drive
    file = service.files().create(
        body=file_metadata,
        media_body=media,
        fields='id, webViewLink'
    ).execute()
    
    # 6. Return success
    return True
```

---

## Scopes Explanation

### Current Scope

```python
DRIVE_SCOPES = ['https://www.googleapis.com/auth/drive']
```

This scope allows:
- ✅ Create files and folders
- ✅ Read files and folders
- ✅ Modify files and folders
- ✅ Delete files and folders

### Other Available Scopes

```
https://www.googleapis.com/auth/drive.readonly
    - Only read access

https://www.googleapis.com/auth/drive.file
    - Access only files created by app

https://www.googleapis.com/auth/drive.appdata
    - Access app data folder only

https://www.googleapis.com/auth/drive.metadata.readonly
    - Only read metadata
```

---

## Error Handling

### Missing Credentials

```python
if not os.path.exists('client_secrets.json'):
    # Show user how to set up
    message = "❌ Google authentication not configured..."
```

### Session Expired

```python
flow = context.user_data.get('google_flow')
if not flow:
    # User waited too long, need new authorization
    message = "❌ Session expired. Please use /google again."
```

### Upload Failures

```python
try:
    file = service.files().create(...).execute()
except HttpError as error:
    # Handle API errors
    print(f"❌ Google Drive upload error: {error}")
    return False
except Exception as e:
    # Handle unexpected errors
    print(f"❌ Unexpected error: {str(e)}")
    return False
```

---

## Security Considerations

### What's Protected

✅ Credentials stored in local JSON files  
✅ No credentials sent over bot  
✅ OAuth tokens only work with Google  
✅ Per-user isolation  

### Token Lifecycle

```
Token Created
    ↓
Valid for 1 hour
    ↓
Refresh Token saved (lasts ~6 months)
    ↓
When token expires, use refresh token
    ↓
Get new token automatically
    ↓
User never sees the process
```

### Revocation

User can revoke anytime:
1. Go to myaccount.google.com/permissions
2. Find ZipperBot
3. Click remove access
4. Done! Next request will fail
5. User can redo `/google` to reconnect

---

## Multi-User Handling

### Each User Independent

```
Bot
├── User 123456 (alice)
│   ├── user_123456_token.json
│   ├── user_123456_folder.json
│   └── Files stored separately
│
├── User 789012 (bob)
│   ├── user_789012_token.json
│   ├── user_789012_folder.json
│   └── Files stored separately
│
└── User 345678 (charlie)
    ├── user_345678_token.json
    ├── user_345678_folder.json
    └── Files stored separately
```

Each user:
- Has their own credentials
- Has their own folder in Google Drive
- Cannot access other users' data
- Can be authenticated/deauthenticated independently

---

## Performance Optimization

### Credential Caching

```python
# Service is created once per request
# Credentials loaded from file (fast)
# Token refresh only if needed
```

### Folder ID Caching

```python
# Folder ID saved after first creation
# No need to search each time
# Just verify it still exists (quick check)
```

### Zip Cleanup

```python
# Temporary zip deleted after upload
# Saves disk space
# User doesn't need local copy (has Google Drive)
```

---

## Debugging

### Enable Logging

Add to bot.py:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Check Credentials File

```python
# Print what's stored
import json
with open('google_credentials/user_123456_token.json', 'r') as f:
    creds = json.load(f)
    print(creds)  # See all credentials
```

### Test Upload Directly

```python
from googleapiclient.http import MediaFileUpload

service = get_google_drive_service(user_id)
file_metadata = {'name': 'test.txt', 'parents': [folder_id]}
media = MediaFileUpload('test.txt', mimetype='text/plain')
file = service.files().create(
    body=file_metadata,
    media_body=media,
    fields='id'
).execute()
print(f"Uploaded: {file.get('id')}")
```

---

## Comparison: OAuth2 vs Service Account

| Aspect | OAuth2 | Service Account |
|--------|--------|-----------------|
| Authentication | User login | App login |
| Credentials | Personal tokens | Shared key |
| Folder access | User's own | Bot admin's |
| Scalability | Per-user | One shared |
| Security | User-isolated | Shared |
| Setup | User-driven | Admin-driven |
| Token refresh | Automatic | Manual |

---

This implementation provides a secure, scalable, and user-friendly way to integrate Google Drive with Telegram bots! 🚀
