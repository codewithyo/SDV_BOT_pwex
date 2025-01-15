import logging
from flask import Flask
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from pw_handler import pw_handler
from kgs_handler import kgs_handler
from config import BOT_TOKEN

logging.basicConfig(format="%(asctime)s - %(message)s", level=logging.INFO)

# Flask App
app = Flask(__name__)

# Owner's Telegram ID (replace with your actual ID)
OWNER_ID = 123456789  # Set the owner's Telegram ID here
allowed_users = set()  # This will store the allowed user IDs
is_function_enabled = False  # This flag will manage the function on/off state

@app.route("/")
def home():
    return "Bot is running on Flask server!"

async def start(update, context):
    await update.message.reply_text("𝐻𝑒𝑙𝑙𝑜 𝑢𝑠𝑒𝑟  😉 𝐼'𝑚 𝐴 𝑆𝑖𝑚𝑝𝑙𝑒 𝐵𝑎𝑡𝑐ℎ 𝑡𝑜 𝑇𝑥𝑇 𝑒𝑥𝑡𝑟𝑎𝑐𝑡𝑜𝑟 𝐵𝑜𝑡\n\n𝑈𝑠𝑒 𝑡ℎ𝑒𝑠𝑒 𝑐𝑜𝑚𝑚𝑎𝑛𝑑𝑠:\n🫠 /pw - 𝑓𝑜𝑟 𝑃𝑊 𝑐𝑜𝑛𝑡𝑒𝑛𝑡\n🫠 /kgs - 𝑓𝑜𝑟 𝑲𝒉𝒂𝒏 𝑮𝒍𝒐𝒃𝒂𝒍 𝑺𝒕𝒖𝒅𝒊𝒆𝒔 𝑐𝑜𝑛𝑡𝑒𝑛𝑡")

async def on_owner(update, context):
    global is_function_enabled
    if update.message.from_user.id == OWNER_ID:
        is_function_enabled = True
        await update.message.reply_text("Owner access enabled! Only allowed users can now interact with the bot.")
    else:
        await update.message.reply_text("You are not the owner of this bot!")

async def off_owner(update, context):
    global is_function_enabled
    if update.message.from_user.id == OWNER_ID:
        is_function_enabled = False
        await update.message.reply_text("Owner access disabled! All users can now interact with the bot.")
    else:
        await update.message.reply_text("You are not the owner of this bot!")

async def add_id(update, context):
    if update.message.from_user.id == OWNER_ID:
        if context.args:  # Check if arguments are provided
            user_id = int(context.args[0])  # Convert the first argument to an integer
            allowed_users.add(user_id)  # Add the user ID to the allowed list
            await update.message.reply_text(f"User ID {user_id} has been added to the allowed list.")
        else:
            await update.message.reply_text("Please provide the user ID to add.")
    else:
        await update.message.reply_text("You are not the owner of this bot!")

# Middleware to check if the function is enabled and if the user is allowed
async def check_permission(update, context):
    if is_function_enabled:
        if update.message.from_user.id not in allowed_users and update.message.from_user.id != OWNER_ID:
            await update.message.reply_text("You are not authorized to use the bot right now.")
            return False  # Deny access
    return True  # Allow access

if __name__ == "__main__":
    from threading import Thread

    # Start Flask server
    flask_thread = Thread(target=lambda: app.run(host="0.0.0.0", port=5000))
    flask_thread.start()

    # Telegram Bot setup
    application = ApplicationBuilder().token(BOT_TOKEN).build()

    # Handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("onowner", on_owner))
    application.add_handler(CommandHandler("offowner", off_owner))
    application.add_handler(CommandHandler("addid", add_id))  # No need for pass_args=True

    # Add the permission check before handling the messages
    application.add_handler(pw_handler)
    application.add_handler(kgs_handler)

    # Start the bot
    application.run_polling()