import os
import zipfile
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, ContextTypes, filters

TOKEN = "8669320374:AAG32jAeg4VKlSox3ty_Vsalfrgqi6hCX5o"

BASE_DIR = "downloads"
ZIP_NAME = "files.zip"

os.makedirs(BASE_DIR, exist_ok=True)

# ذخیره فایل‌های دریافتی
async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    file = update.message.document or update.message.audio

    if not file:
        await update.message.reply_text("فقط فایل بفرست.")
        return

    file_obj = await context.bot.get_file(file.file_id)

    file_path = os.path.join(BASE_DIR, file.file_name)
    await file_obj.download_to_drive(file_path)

    await update.message.reply_text(f"گرفتم: {file.file_name}")


# ساخت zip
async def make_zip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    zip_path = os.path.join(BASE_DIR, ZIP_NAME)

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(BASE_DIR):
            for f in files:
                if f == ZIP_NAME:
                    continue
                full_path = os.path.join(root, f)
                zipf.write(full_path, arcname=f)

    await update.message.reply_document(document=open(zip_path, "rb"))

    # پاکسازی بعد از ارسال (اختیاری)
    for root, _, files in os.walk(BASE_DIR):
        for f in files:
            if f != ZIP_NAME:
                os.remove(os.path.join(root, f))


# پیام راهنما
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "فایل‌ها رو بفرست.\nوقتی تموم شد /zip بزن."
    )


app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("zip", make_zip))
app.add_handler(MessageHandler(filters.Document.ALL | filters.AUDIO, handle_file))

app.run_polling()