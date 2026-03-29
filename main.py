import os
import asyncio
import logging
from flask import Flask
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# --- LOGGING ---
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# --- CONFIG ---
TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", 0))

# --- FLASK ---
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is Running 24/7!"

@app.route('/health')
def health():
    return "OK", 200

# --- BOT HANDLERS ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"Hello {update.effective_user.first_name}!\nBot active hai. Kiya bolna chahoge?")

async def handle_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id == ADMIN_ID:
        if update.message.reply_to_message:
            try:
                msg_text = update.message.reply_to_message.text or update.message.reply_to_message.caption
                target_id = msg_text.split("ID: ")[1].split("\n")[0].strip()
                await update.message.copy(chat_id=target_id)
            except Exception as e:
                logging.error(f"Reply Error: {e}")
                await update.message.reply_text("❌ Error: Reply ke liye ID wala message select karein.")
    else:
        header = f"📩 **New Message**\nID: {user_id}\nName: {update.effective_user.first_name}\n\n"
        try:
            # Send to Admin
            if update.message.text:
                await context.bot.send_message(chat_id=ADMIN_ID, text=header + update.message.text)
            else:
                await context.bot.send_message(chat_id=ADMIN_ID, text=header)
                await update.message.copy(chat_id=ADMIN_ID)
        except Exception as e:
            logging.error(f"Forward Error: {e}")

# --- ASYNC BOT STARTUP ---
async def start_bot():
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, handle_chat))
    
    await application.initialize()
    await application.start()
    await application.updater.start_polling()
    logging.info("Telegram Bot Started Successfully!")

# This starts the bot in the background loop
try:
    loop = asyncio.get_event_loop()
except RuntimeError:
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

loop.create_task(start_bot())

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
