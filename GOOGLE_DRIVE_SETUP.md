# Google Drive Setup Guide for ZipperBot

This guide will help you set up Google Drive integration for automatic zip file uploads.

## Step 1: Create a Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Click on the project dropdown at the top
3. Click "NEW PROJECT"
4. Enter project name: `ZipperBot` (or your preferred name)
5. Click "CREATE"
6. Wait for the project to be created

## Step 2: Enable Google Drive API

1. In the Google Cloud Console, go to "APIs & Services" > "Library"
2. Search for "Google Drive API"
3. Click on "Google Drive API"
4. Click the "ENABLE" button
5. Wait for it to be enabled

## Step 3: Create Service Account

1. Go to "APIs & Services" > "Credentials"
2. Click "CREATE CREDENTIALS" at the top
3. Select "Service Account"
4. Fill in the form:
   - Service account name: `ZipperBot`
   - Click "CREATE AND CONTINUE"
5. Skip the optional steps (click "CONTINUE")
6. Click "CREATE KEY"
7. Choose "JSON" format
8. Click "CREATE"
9. The JSON file will automatically download

## Step 4: Add Credentials to Your Project

1. Copy the downloaded JSON file to your ZipperBot project root
2. Rename it to `credentials.json` (if it has a different name)
3. Your file structure should look like:
   ```
   ZipperBot/
   ├── bot.py
   ├── credentials.json
   ├── .env
   ├── requirements.txt
   └── ...
   ```

## Step 5: Create Google Drive Folder

1. Open [Google Drive](https://drive.google.com)
2. Click "New" > "Folder"
3. Name it `ZipperBot Archives` (or any name you prefer)
4. Right-click the folder and select "Share"
5. In the sharing dialog, find your service account email
6. It should look like: `zipperbot@your-project-id.iam.gserviceaccount.com`
7. Grant "Editor" access to this account
8. Click "Share"

## Step 6: Get Your Folder ID

1. Open your newly created folder in Google Drive
2. Look at the URL in the address bar:
   ```
   https://drive.google.com/drive/folders/ABC123XYZ456
                                           ^
                                    Folder ID
   ```
3. Copy the folder ID (the long string after `/folders/`)

## Step 7: Configure .env File

1. Open the `.env` file in your ZipperBot project
2. Add your folder ID:
   ```env
   TELEGRAM_BOT_TOKEN=your_token_here
   GOOGLE_DRIVE_FOLDER_ID=your_folder_id_here
   ```
3. Save the file

## Step 8: Test the Setup

1. Start your bot:
   ```bash
   python bot.py
   ```

2. In Telegram:
   - Send `/start` to your bot
   - Send a test file
   - Send `/archive`
   - Enter a filename (e.g., "test_archive")
   - Watch for the upload message

3. Check your Google Drive folder to verify the zip file was uploaded

## Troubleshooting

### "credentials.json not found"
- Make sure the file is in the project root directory
- Check the filename is exactly `credentials.json`

### "Google Drive upload failed"
- Verify the service account has "Editor" access to the folder
- Check that `GOOGLE_DRIVE_FOLDER_ID` is correct in `.env`
- Try re-sharing the folder with the service account

### Permission denied errors
- Regenerate the service account key
- Re-share the folder with the new service account email

### Folder ID not working
- Copy the folder ID again from the URL
- Make sure there are no extra spaces or characters

## Finding Your Service Account Email

If you need to find your service account email again:

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Go to "APIs & Services" > "Service Accounts"
3. Click on the service account you created
4. Look for the "Email" field - that's your service account email

## Security Notes

- Keep your `credentials.json` file secure
- Add it to `.gitignore` to prevent accidental commits
- Don't share this file with others
- The service account can only access folders you explicitly share with it

## Using Without Google Drive

If you don't want to set up Google Drive:

1. Just leave `GOOGLE_DRIVE_FOLDER_ID` empty in `.env`
2. The bot will still work perfectly
3. Zip files will only be sent to Telegram (no Google Drive backup)

The bot will show a friendly message if Google Drive isn't configured, and will continue working normally.

---

**Need help?** Check the main [README.md](README.md) for more information.
