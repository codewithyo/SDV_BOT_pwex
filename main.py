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
    BOT_TOKEN = "8071764665:AAF5zG5aZtfA0fWAPbDm14LDGbbLxs-dcN0"
    application = ApplicationBuilder().token(BOT_TOKEN).build()

    # Handlers
    async def start(update, context):
        await update.message.reply_text("𝐻𝑒𝑙𝑙𝑜 𝑢𝑠𝑒𝑟  😉 𝐼'𝑚 𝐴 𝑆𝑖𝑚𝑝𝑙𝑒 𝐵𝑎𝑡𝑐ℎ 𝑡𝑜 𝑇𝑥𝑇 𝑒𝑥𝑡𝑟𝑎𝑐𝑡𝑜𝑟 𝐵𝑜𝑡\n\n𝑈𝑠𝑒 𝑡ℎ𝑖𝑠 𝑐𝑜𝑚𝑚𝑎𝑛𝑑🫠 /𝑝𝑤 𝑎𝑛𝑑 𝑠𝑒𝑛𝑑 𝑦𝑜𝑢𝑟 𝑎𝑢𝑡ℎ_𝑐𝑜𝑑𝑒 [𝑇𝑜𝑘𝑒𝑛]💢")

    application.add_handler(CommandHandler("start", start))
    application.add_handler(pw_handler)  # Adding /pw command handler

    # Run Bot
    application.run_polling()