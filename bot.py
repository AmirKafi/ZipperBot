import os
import zipfile
import json
import shutil
from pathlib import Path
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload

# Load environment variables
load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

# Storage directory for user files
TEMP_DIR = 'user_files'
CREDENTIALS_DIR = 'google_credentials'
DRIVE_SCOPES = ['https://www.googleapis.com/auth/drive']

# Conversation states
AWAITING_FILENAME = 1


def ensure_credentials_dir():
    """Ensure credentials directory exists."""
    os.makedirs(CREDENTIALS_DIR, exist_ok=True)


def get_user_credentials_path(user_id: int) -> str:
    """Get the path to user's Google credentials file."""
    ensure_credentials_dir()
    return os.path.join(CREDENTIALS_DIR, f'user_{user_id}_token.json')


def get_user_drive_folder_path(user_id: int) -> str:
    """Get the path to user's Drive folder ID file."""
    ensure_credentials_dir()
    return os.path.join(CREDENTIALS_DIR, f'user_{user_id}_folder.json')


def get_google_drive_service(user_id: int):
    """Get Google Drive service for user."""
    creds_path = get_user_credentials_path(user_id)
    
    try:
        # Check if user has valid credentials
        if os.path.exists(creds_path):
            creds = Credentials.from_authorized_user_file(creds_path, DRIVE_SCOPES)
            
            # Refresh if needed
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
                # Save refreshed credentials
                with open(creds_path, 'w') as token:
                    token.write(creds.to_json())
            
            return build('drive', 'v3', credentials=creds)
    except Exception as e:
        print(f"❌ Error getting Drive service: {str(e)}")
    
    return None


def get_or_create_zipper_folder(user_id: int, service) -> str:
    """Get or create ZipperBot folder in user's Google Drive."""
    try:
        folder_info_path = get_user_drive_folder_path(user_id)
        
        # Check if we already have the folder ID
        if os.path.exists(folder_info_path):
            with open(folder_info_path, 'r') as f:
                folder_info = json.load(f)
                folder_id = folder_info.get('folder_id')
                
                # Verify folder still exists
                if folder_id:
                    try:
                        service.files().get(fileId=folder_id).execute()
                        return folder_id
                    except:
                        pass  # Folder doesn't exist, create new one
        
        # Create new folder
        file_metadata = {
            'name': 'ZipperBot Archives',
            'mimeType': 'application/vnd.google-apps.folder'
        }
        
        folder = service.files().create(body=file_metadata, fields='id').execute()
        folder_id = folder.get('id')
        
        # Save folder ID
        folder_info = {'folder_id': folder_id}
        with open(folder_info_path, 'w') as f:
            json.dump(folder_info, f)
        
        return folder_id
    except Exception as e:
        print(f"❌ Error managing Drive folder: {str(e)}")
        return None


def upload_to_google_drive(user_id: int, zip_path: str, filename: str) -> bool:
    """Upload zip file to user's Google Drive."""
    try:
        service = get_google_drive_service(user_id)
        if not service:
            return False
        
        # Get or create folder
        folder_id = get_or_create_zipper_folder(user_id, service)
        if not folder_id:
            return False
        
        # Upload file
        file_metadata = {
            'name': f"{filename}.zip",
            'parents': [folder_id]
        }
        
        media = MediaFileUpload(zip_path, mimetype='application/zip')
        
        file = service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id, webViewLink'
        ).execute()
        
        print(f"✅ File uploaded to Google Drive: {file.get('webViewLink')}")
        return True
    except HttpError as error:
        print(f'❌ Google Drive upload error: {error}')
        return False
    except Exception as e:
        print(f'❌ Unexpected error during upload: {str(e)}')
        return False


def user_has_google_connected(user_id: int) -> bool:
    """Check if user has Google Drive connected."""
    creds_path = get_user_credentials_path(user_id)
    return os.path.exists(creds_path)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    user_id = update.message.from_user.id
    
    google_status = "✅ Connected" if user_has_google_connected(user_id) else "❌ Not Connected"
    
    welcome_message = f"""
👋 Welcome to ZipperBot!

I can help you archive your files and create zip files.

📝 How to use:
1. Send me any files you want to archive
2. Type /archive to create a zip file from all your files
3. Choose a filename for your zip
4. I'll upload the zip file back to you
5. ☁️ Bonus: The zip will also be uploaded to Google Drive!

📋 Available commands:
/start - Show this message
/archive - Create and send zip file of all your files
/clear - Delete all your files and start fresh
/google - Connect to Google Drive
/help - Show help message

☁️ Google Drive Status: {google_status}
    """
    await update.message.reply_text(welcome_message)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    help_text = """
🤖 ZipperBot Help

This bot allows you to:
• Send multiple files to the bot
• Archive them into a single zip file
• Download the zip file directly from Telegram
• ☁️ Automatically upload to Google Drive

Commands:
/start - Show welcome message
/archive - Create zip file from all uploaded files
/google - Connect to your Google Drive account
/clear - Delete all files and start over
/help - Show this message

Examples:
1. Send a photo → Send a document → Send another file → /archive → Choose filename → Get zip

Features:
✨ Telegram Download - Get zip directly in Telegram
☁️ Google Drive Upload - Automatically saves to your Google Drive
📝 Custom Filenames - Choose your own zip file name
🔐 Easy Authentication - Just click the login link!

⚠️ Note: Files are stored temporarily and can be cleared with /clear
    """
    await update.message.reply_text(help_text)


async def google_login(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle Google Drive authentication."""
    user_id = update.message.from_user.id
    
    # Check if client_secrets.json exists
    if not os.path.exists('client_secrets.json'):
        await update.message.reply_text(
            "❌ Google authentication not configured.\n\n"
            "Please set up OAuth credentials:\n"
            "1. Go to https://console.cloud.google.com\n"
            "2. Create a new project\n"
            "3. Enable Google Drive API\n"
            "4. Create OAuth 2.0 Desktop Application credentials\n"
            "5. Download as JSON and save as 'client_secrets.json' in the bot folder"
        )
        return
    
    try:
        # Check if already connected
        if user_has_google_connected(user_id):
            service = get_google_drive_service(user_id)
            if service:
                await update.message.reply_text("✅ You are already connected to Google Drive!")
                return
        
        # Generate auth URL
        flow = InstalledAppFlow.from_client_secrets_file(
            'client_secrets.json',
            scopes=DRIVE_SCOPES
        )
        
        auth_url, _ = flow.authorization_url(prompt='consent')
        
        # For simplicity, we'll store the flow temporarily
        context.user_data['google_flow'] = flow
        context.user_data['google_user_id'] = user_id
        
        # Send login link
        await update.message.reply_text(
            "🔐 Click the link below to connect your Google Drive account:\n\n"
            f"{auth_url}\n\n"
            "After you authorize, you'll get a code. Send it to me!"
        )
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")


async def handle_google_code(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle authorization code from user."""
    user_id = update.message.from_user.id
    auth_code = update.message.text.strip()
    
    # Check if this looks like an auth code
    if not auth_code or len(auth_code) < 10:
        await update.message.reply_text(
            "⚠️ This doesn't look like an authorization code.\n\n"
            "Please make sure you:\n"
            "1. Clicked the login link\n"
            "2. Authorized the app\n"
            "3. Copied the entire authorization code\n"
            "4. Pasted it here"
        )
        return
    
    try:
        flow = context.user_data.get('google_flow')
        if not flow:
            await update.message.reply_text("❌ Session expired. Please use /google again.")
            return
        
        # Exchange code for credentials
        flow.fetch_token(code=auth_code)
        creds = flow.credentials
        
        # Save credentials
        creds_path = get_user_credentials_path(user_id)
        with open(creds_path, 'w') as token:
            token.write(creds.to_json())
        
        await update.message.reply_text(
            "✅ Successfully connected to Google Drive!\n\n"
            "Now when you use /archive, your zip files will be automatically uploaded to Google Drive.\n\n"
            "Use /start to continue."
        )
    except Exception as e:
        await update.message.reply_text(f"❌ Authentication failed: {str(e)}")


async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle incoming files from users."""
    user_id = update.message.from_user.id
    user_folder = os.path.join(TEMP_DIR, str(user_id))
    
    # Create user-specific folder
    os.makedirs(user_folder, exist_ok=True)
    
    # Determine file type and get it
    file_info = None
    filename = None
    
    if update.message.document:
        file_info = update.message.document
        filename = update.message.document.file_name
    elif update.message.photo:
        file_info = update.message.photo[-1]  # Get highest resolution
        filename = f"photo_{len(os.listdir(user_folder))}.jpg"
    elif update.message.video:
        file_info = update.message.video
        filename = f"video_{update.message.video.file_id[:8]}.mp4"
    elif update.message.audio:
        file_info = update.message.audio
        filename = f"audio_{update.message.audio.file_id[:8]}.mp3"
    elif update.message.voice:
        file_info = update.message.voice
        filename = f"voice_{update.message.voice.file_id[:8]}.ogg"
    else:
        await update.message.reply_text("❌ Unsupported file type. Please send documents, photos, videos, or audio files.")
        return
    
    try:
        # Download file
        file = await context.bot.get_file(file_info.file_id)
        file_path = os.path.join(user_folder, filename)
        await file.download_to_drive(file_path)
        
        # Count files
        file_count = len(os.listdir(user_folder))
        await update.message.reply_text(
            f"✅ File received and saved!\n\n"
            f"📦 Total files: {file_count}\n"
            f"📝 Latest: {filename}\n\n"
            f"Send /archive to create a zip file."
        )
    except Exception as e:
        await update.message.reply_text(f"❌ Error downloading file: {str(e)}")


async def archive_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Start the archive process and ask for filename."""
    user_id = update.message.from_user.id
    user_folder = os.path.join(TEMP_DIR, str(user_id))
    
    # Check if user has any files
    if not os.path.exists(user_folder) or not os.listdir(user_folder):
        await update.message.reply_text("❌ No files found. Please send some files first.")
        return ConversationHandler.END
    
    # Store user_id in context for later use
    context.user_data['archive_user_id'] = user_id
    
    # Ask for filename
    await update.message.reply_text(
        "📝 What would you like to name your zip file?\n\n"
        "Example: my_documents, backup_2024, travel_photos\n\n"
        "Type /cancel to cancel archiving."
    )
    return AWAITING_FILENAME


async def receive_filename(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Receive filename from user and create archive."""
    filename = update.message.text.strip()
    
    # Validate filename
    invalid_chars = '<>:"|?*'
    if any(char in filename for char in invalid_chars):
        await update.message.reply_text(
            "❌ Invalid characters in filename.\n"
            f"Please avoid: {invalid_chars}\n\n"
            "Try again:"
        )
        return AWAITING_FILENAME
    
    if not filename or len(filename) > 50:
        await update.message.reply_text(
            "❌ Filename must be between 1 and 50 characters.\n\n"
            "Try again:"
        )
        return AWAITING_FILENAME
    
    user_id = context.user_data['archive_user_id']
    user_folder = os.path.join(TEMP_DIR, str(user_id))
    
    try:
        # Show progress
        await update.message.reply_text(f"⏳ Creating '{filename}.zip'... Please wait.")
        
        # Create zip file with user-chosen filename
        zip_filename = f"{filename}.zip"
        zip_path = os.path.join(TEMP_DIR, zip_filename)
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file in os.listdir(user_folder):
                file_path = os.path.join(user_folder, file)
                if os.path.isfile(file_path):
                    zipf.write(file_path, arcname=file)
        
        # Get file size
        file_size = os.path.getsize(zip_path)
        size_mb = file_size / (1024 * 1024)
        
        # Send zip file
        with open(zip_path, 'rb') as zip_file:
            await update.message.reply_document(
                document=zip_file,
                filename=zip_filename,
                caption=f"📦 Your archive: {filename}.zip\n📊 Size: {size_mb:.2f} MB"
            )
        
        # Try to upload to Google Drive if connected
        if user_has_google_connected(user_id):
            await update.message.reply_text("☁️ Uploading to Google Drive...")
            if upload_to_google_drive(user_id, zip_path, filename):
                await update.message.reply_text("✅ File successfully uploaded to Google Drive!")
            else:
                await update.message.reply_text(
                    "⚠️ File sent to Telegram but Google Drive upload failed.\n"
                    "Try reconnecting with /google"
                )
        else:
            await update.message.reply_text(
                "ℹ️ Zip not uploaded to Google Drive.\n"
                "Use /google to connect your Google Drive account for automatic backups!"
            )
        
        # Clean up zip file
        os.remove(zip_path)
        
        # Final message
        await update.message.reply_text(
            "✅ Done!\n\n"
            "Use /clear to delete files and /start to see options."
        )
        
    except Exception as e:
        await update.message.reply_text(f"❌ Error creating zip file: {str(e)}")
    
    return ConversationHandler.END


async def cancel_archive(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancel the archive operation."""
    await update.message.reply_text("❌ Archive cancelled. Use /archive to try again.")
    return ConversationHandler.END


async def clear_files(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Delete all files for the user."""
    user_id = update.message.from_user.id
    user_folder = os.path.join(TEMP_DIR, str(user_id))
    
    try:
        if os.path.exists(user_folder):
            shutil.rmtree(user_folder)
            await update.message.reply_text("✅ All your files have been deleted.")
        else:
            await update.message.reply_text("ℹ️ No files to delete.")
    except Exception as e:
        await update.message.reply_text(f"❌ Error deleting files: {str(e)}")


def main() -> None:
    """Start the bot."""
    if not TELEGRAM_BOT_TOKEN:
        print("❌ Error: TELEGRAM_BOT_TOKEN not found in .env file")
        print("Please set your bot token in the .env file")
        return
    
    # Create the Application
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Create archive conversation handler
    archive_conv_handler = ConversationHandler(
        entry_points=[CommandHandler('archive', archive_start)],
        states={
            AWAITING_FILENAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_filename)],
        },
        fallbacks=[CommandHandler('cancel', cancel_archive)],
    )

    # Add command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("google", google_login))
    application.add_handler(archive_conv_handler)
    application.add_handler(CommandHandler("clear", clear_files))

    # Add file handler
    application.add_handler(MessageHandler(
        filters.Document | filters.Photo | filters.Video | filters.Audio | filters.Voice,
        handle_file
    ))
    
    # Add fallback for authorization codes
    application.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        handle_google_code
    ))

    # Run the bot
    print("🚀 ZipperBot is starting...")
    application.run_polling()


if __name__ == '__main__':
    main()
