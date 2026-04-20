import os
import zipfile
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, ContextTypes, filters

TOKEN = "YOUR_BOT_TOKEN"

BASE_DIR = "files"
os.makedirs(BASE_DIR, exist_ok=True)

user_files = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "فایل‌هاتو بفرست. بعدش /done بزن تا زیپ کنم."
    )

async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id

    if user_id not in user_files:
        user_files[user_id] = []

    doc = update.message.document
    file = await doc.get_file()

    save_path = os.path.join(BASE_DIR, f"{user_id}_{doc.file_name}")
    await file.download_to_drive(save_path)

    user_files[user_id].append(save_path)

    await update.message.reply_text(f"گرفتم ✔️ ({len(user_files[user_id])})")

async def done(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    files = user_files.get(user_id, [])

    if not files:
        await update.message.reply_text("هیچ فایلی ندادی.")
        return

    zip_path = os.path.join(BASE_DIR, f"{user_id}.zip")

    with zipfile.ZipFile(zip_path, "w") as zipf:
        for f in files:
            zipf.write(f, os.path.basename(f))

    await update.message.reply_document(document=open(zip_path, "rb"))

    # cleanup
    for f in files:
        os.remove(f)
    os.remove(zip_path)
    user_files[user_id] = []

async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    user_files[user_id] = []
    await update.message.reply_text("ریست شد.")

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("done", done))
app.add_handler(CommandHandler("reset", reset))
app.add_handler(MessageHandler(filters.Document.ALL, handle_file))

app.run_polling()