import logging
import random
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters

# Enable logging (important for Telegram hosting logs)
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# === CONFIGURATION ===
import os
BOT_TOKEN = os.getenv("BOT_TOKEN", "8272480358:AAFkydAtheWxTSO5Q0zW7N04i7Wa110bpSo")
EMOJIS = [
    "😂", "❤️", "🔥", "👍", "😍", "😎", "💯", "🥰", "🎉", "😮", "🤖",
    "😢", "😡", "😱", "🤔", "🥳", "💖", "🙌", "👏", "😏", "🤩",
    "😇", "💤", "😴", "😜", "🥶", "😳", "🤣", "😛", "💫", "💥",
    "💌", "🧿", "🌟", "🍀", "☄️", "💎", "🤡", "😱", "🤬", "☠"
]
# === HANDLERS ===
async def auto_react(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return

    chat_id = update.message.chat_id
    message_id = update.message.message_id
    emoji = random.choice(EMOJIS)

    try:
        await context.bot.set_message_reaction(
            chat_id=chat_id,
            message_id=message_id,
            reaction=[emoji]
        )
        logger.info(f"Reacted with {emoji} in chat {chat_id}")
    except Exception as e:
        logger.error(f"Reaction failed: {e}")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🤖 Auto Reaction Bot is online and reacting to all messages!")

# === MAIN FUNCTION ===
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.COMMAND & filters.Regex("^/start$"), start))
    app.add_handler(MessageHandler(filters.ALL, auto_react))

    logger.info("🚀 Bot is now running and ready to react!")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()