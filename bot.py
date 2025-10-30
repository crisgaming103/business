import telebot
from telebot import types
import json
import os
import random
import threading
import time
import requests
import io

# ===================== #
#     BOT SETTINGS      #
# ===================== #
BOT_TOKEN = "8210989428:AAEmQW5V1fsYTSLDQzxv6_KaiUX5ZLQOHLI"
bot = telebot.TeleBot(BOT_TOKEN)

OWNER_ID = 6784382795
ACCESS_KEY = "Cris-rank-2025"
WELCOME_FILE = "welcome_messages.json"

user_balance = {}

# ===================== #
#   AUTO DELETE SYSTEM  #
# ===================== #
def send_and_auto_delete(chat_id, text, delay=10):
    msg = bot.send_message(chat_id, text)
    threading.Thread(target=auto_delete, args=(chat_id, msg.message_id, delay), daemon=True).start()

def auto_delete(chat_id, msg_id, delay=10):
    time.sleep(delay)
    try:
        bot.delete_message(chat_id, msg_id)
    except Exception:
        pass

# ===================== #
#     START COMMAND     #
# ===================== #
@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    username = message.from_user.username
    first_name = message.from_user.first_name

    if user_id not in user_balance:
        user_balance[user_id] = 100  # default balance

    welcome_text = (
        f"👋 Hello {first_name}!\n\n"
        "Welcome to **CrisBot Elite Portal**.\n"
        "Use /menu to access your King Rank panel."
    )
    bot.reply_to(message, welcome_text)

# ===================== #
#    BALANCE COMMAND    #
# ===================== #
@bot.message_handler(commands=['balance'])
def check_balance(message):
    bal = user_balance.get(message.from_user.id, 0)
    if bal == float('inf'):
        send_and_auto_delete(message.chat.id, "💰 You have unlimited balance!")
    else:
        send_and_auto_delete(message.chat.id, f"💰 Your balance: {bal}")

# ===================== #
#   INLINE MENU (KEY)   #
# ===================== #
def send_inline_menu(user_id, username, name):
    if user_balance.get(user_id, 0) <= 0:
        return False

    info_text = (
        "👑 **Welcome to the Cris King Rank Portal** 👑\n"
        "━━━━━━━━━━━━━━━━━━━━━━━\n"
        "🎮 *Elite Access Credentials:*\n\n"
        f"👤 **Name:** {name}\n"
        f"💬 **Username:** @{username if username else 'N/A'}\n"
        f"🆔 **User ID:** `{user_id}`\n"
        f"🔑 **Access Key:** `{ACCESS_KEY}`\n\n"
        "⚔️ *This key grants you verified entry into the exclusive* **King Rank Network**.\n"
        "🔒 Keep your credentials confidential.\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━━\n"
        "🏆 **About King Rank**\n"
        "🔥 You’ve entered the elite circle of Cris players.\n"
        "💠 *Privileges:*\n"
        "• Early access to features\n"
        "• Priority in-game tools\n"
        "• Recognition among King Rank elites\n\n"
        "🚀 Tap below to open your **King Rank Control Center**."
    )

    target_url = "https://business-ten-lac.vercel.app/"
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("👑 Open King Rank Portal", url=target_url))

    msg = bot.send_message(user_id, info_text, parse_mode="Markdown", reply_markup=markup)
    threading.Thread(target=auto_delete, args=(user_id, msg.message_id), daemon=True).start()
    return True

# ===================== #
#       MENU CMD        #
# ===================== #
@bot.message_handler(commands=['menu'])
def menu(message):
    user = message.from_user
    if send_inline_menu(user.id, user.username, user.first_name):
        send_and_auto_delete(message.chat.id, "✅ Menu sent! Check your private chat.")
    else:
        send_and_auto_delete(message.chat.id, "❌ You have no balance.")

# ===================== #
#      AI SYSTEM        #
# ===================== #
def ai_response(prompt):
    try:
        url = "https://api-inference.huggingface.co/models/facebook/blenderbot-400M-distill"
        headers = {"Authorization": "Bearer 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"}
        payload = {"inputs": prompt}
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        data = response.json()
        if isinstance(data, list) and len(data) > 0 and "generated_text" in data[0]:
            return data[0]["generated_text"]
        return "🤖 AI: Sorry, I couldn’t think of a reply."
    except Exception:
        return "⚠️ AI temporarily unavailable."

@bot.message_handler(func=lambda msg: True)
def handle_message(message):
    user_id = message.from_user.id
    text = message.text
    if user_balance.get(user_id, 0) <= 0:
        send_and_auto_delete(message.chat.id, "❌ You have no balance left.")
        return

    reply = ai_response(text)
    bot.reply_to(message, reply)

# ===================== #
#      BOT POLLING      #
# ===================== #
print("🤖 CrisBot with Auto AI + Inline Portal running...")

while True:
    try:
        bot.infinity_polling(timeout=60, long_polling_timeout=30)
    except Exception as e:
        print(f"⚠️ Bot error, restarting: {e}")
        time.sleep(5)
