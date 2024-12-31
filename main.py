import logging
from flask import Flask
from telegram.ext import ApplicationBuilder, CommandHandler
from pw_handler import pw_handler  # Importing pw_handler

# Logging Setup
logging.basicConfig(format="%(asctime)s - %(message)s", level=logging.INFO)

# Flask App
app = Flask(__name__)

@app.route("/")
def home():
    return "Bot is running on Flask server!"

if __name__ == "__main__":
    from threading import Thread

    # Start Flask server
    flask_thread = Thread(target=lambda: app.run(host="0.0.0.0", port=5000))
    flask_thread.start()

    # Telegram Bot setup
    BOT_TOKEN = "USER_BOT_TOKEN"
    application = ApplicationBuilder().token(BOT_TOKEN).build()

    # Handlers
    async def start(update, context):
        await update.message.reply_text("Hi! Use /pw to start processing your batches.")

    application.add_handler(CommandHandler("start", start))
    application.add_handler(pw_handler)  # Adding /pw command handler

    # Run Bot
    application.run_polling()