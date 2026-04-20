import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
from utils.zipper import create_zip

TOKEN = os.environ.get("BOT_TOKEN")

# ذخیره موقت در RAM (محدود به اجرای سرورلس)
user_files = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("فایل‌ها رو بفرست، آخرش /zip بزن.")

async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id

    file = update.message.document or update.message.audio
    if not file:
        return

    file_obj = await context.bot.get_file(file.file_id)

    os.makedirs("/tmp", exist_ok=True)
    path = f"/tmp/{file.file_unique_id}_{file.file_name}"

    await file_obj.download_to_drive(path)

    user_files.setdefault(user_id, []).append(path)

    await update.message.reply_text("گرفتم ✔️")

async def make_zip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id

    files = user_files.get(user_id, [])

    if not files:
        await update.message.reply_text("هیچی ندادی.")
        return

    zip_buffer = create_zip(files)

    await update.message.reply_document(
        document=zip_buffer,
        filename="files.zip"
    )

    # پاکسازی
    user_files[user_id] = []

def get_app():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("zip", make_zip))
    app.add_handler(MessageHandler(filters.Document.ALL | filters.AUDIO, handle_file))

    return app

app = get_app()

async def handler(request):
    return await app.update_queue.put(
        Update.de_json(await request.json(), app.bot)
    )