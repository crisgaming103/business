import telebot
from telebot import types
import json
import os
import random
from telebot.types import ChatPermissions

BOT_TOKEN = "8210989428:AAEmQW5V1fsYTSLDQzxv6_KaiUX5ZLQOHLI"
bot = telebot.TeleBot(BOT_TOKEN)

OWNER_ID = 6784382795
ACCESS_KEY = "Cris-rank-2025"
WELCOME_FILE = "welcome_messages.json"

# --- Load or Create Welcome File ---
if not os.path.exists(WELCOME_FILE):
    with open(WELCOME_FILE, "w") as f:
        json.dump({}, f, indent=4)

def load_welcome():
    with open(WELCOME_FILE, "r") as f:
        return json.load(f)

def save_welcome(data):
    with open(WELCOME_FILE, "w") as f:
        json.dump(data, f, indent=4)

# --- Admin Check ---
def is_admin_or_owner(chat_id, user_id):
    if user_id == OWNER_ID:
        return True
    try:
        admins = [admin.user.id for admin in bot.get_chat_administrators(chat_id)]
        return user_id in admins
    except:
        return False

# --- Balance System ---
user_balance = {}
user_warnings = {}

def has_balance(user_id):
    """Check if the user has sufficient balance"""
    bal = user_balance.get(user_id, 0)
    return bal > 0 or bal == float('inf')

@bot.message_handler(commands=['give'])
def give_balance(message):
    if message.from_user.id != OWNER_ID:
        return bot.reply_to(message, "🚫 Only the owner can give balance.")
    if message.reply_to_message:
        target_user = message.reply_to_message.from_user
    else:
        args = message.text.split()
        if len(args) < 2 or not args[1].isdigit():
            return bot.reply_to(message, "⚠️ Usage: /give <user_id> or reply")
        target_user = type('User', (), {'id': int(args[1]), 'first_name': f'User {args[1]}'})()
    user_balance[target_user.id] = float('inf')
    bot.reply_to(message, f"✅ {target_user.first_name} now has unlimited balance!")

@bot.message_handler(commands=['balance'])
def check_balance(message):
    bal = user_balance.get(message.from_user.id, 0)
    if bal == float('inf'):
        bot.reply_to(message, "💰 You have unlimited balance!")
    else:
        bot.reply_to(message, f"💰 Your balance: {bal}")

# --- Inline Menu ---
def send_inline_menu(user_id, username, name):
    if not has_balance(user_id):
        bot.send_message(user_id, "🚫 You do not have enough balance to access the portal.\n💳 Contact the admin to top up your account.")
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
        "🔒 Please keep your access credentials confidential at all times.\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━━\n"
        "🏆 **About King Rank**\n"
        "🔥 You’ve entered the elite circle of Cris players — the top-tier community of strategy, skill, and dedication.\n"
        "💠 *Your privileges include:*\n"
        "• Early access to new tools\n"
        "• VIP priority support\n"
        "• Exclusive customization rights\n\n"
        "🚀 Tap below to open your **King Rank Control Center.**"
    )

    target_url = "https://business-ten-lac.vercel.app/"
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("👑 Enter King Rank Portal", url=target_url))

    bot.send_message(user_id, info_text, parse_mode="Markdown", reply_markup=markup)
    return True

# --- Menu Command ---
@bot.message_handler(commands=['menu'])
def menu(message):
    user = message.from_user
    if send_inline_menu(user.id, user.username, user.first_name):
        bot.reply_to(message, "✅ Portal link sent! Check your private chat.")
    else:
        bot.reply_to(message, "❌ You have no balance or access.")

# --- Start Command (Protected) ---
@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    if not has_balance(user_id):
        return bot.reply_to(message, "🚫 **Access Denied**\nYou currently have **no balance** to use this bot.\n💳 Please contact the admin to recharge.", parse_mode="Markdown")

    bot.reply_to(
        message,
        f"👋 Hello {message.from_user.first_name}!\nWelcome to **Cris King Rank Bot.**\nUse /menu to access your control panel.",
        parse_mode="Markdown"
    )

# --- Help Command ---
@bot.message_handler(commands=['help'])
def help_cmd(message):
    if not has_balance(message.from_user.id) and message.from_user.id != OWNER_ID:
        return bot.reply_to(message, "🚫 You have no balance to access commands.")
    text = (
        "🤖 **Cris King Rank Bot Commands**\n\n"
        "🛡 **Admin & Owner Tools**\n"
        "/warn /unwarn /mute /unmute /kick /ban /unban\n\n"
        "💰 **Balance System**\n"
        "/give /balance /menu\n\n"
        "ℹ️ **Utilities**\n"
        "/id /info /rules\n\n"
        "🎉 **Fun**\n"
        "/hug /slap /quote"
    )
    bot.reply_to(message, text, parse_mode="Markdown")

# --- Info & Fun Commands (Protected) ---
def command_requires_balance(func):
    def wrapper(message):
        if not has_balance(message.from_user.id) and message.from_user.id != OWNER_ID:
            bot.reply_to(message, "🚫 You must have balance to use this command.")
            return
        func(message)
    return wrapper

@bot.message_handler(commands=['id'])
@command_requires_balance
def get_id(message):
    bot.reply_to(message, f"🆔 Your ID: `{message.from_user.id}`", parse_mode="Markdown")

@bot.message_handler(commands=['info'])
@command_requires_balance
def info(message):
    target = message.reply_to_message.from_user if message.reply_to_message else message.from_user
    username = f"@{target.username}" if target.username else "❌ No username"
    bot.reply_to(message, f"👤 Name: {target.first_name}\n💬 Username: {username}\n🆔 ID: `{target.id}`", parse_mode="Markdown")

@bot.message_handler(commands=['hug'])
@command_requires_balance
def hug(message):
    target = message.reply_to_message.from_user.first_name if message.reply_to_message else "everyone"
    bot.reply_to(message, f"🤗 {message.from_user.first_name} hugged {target}! 💞")

@bot.message_handler(commands=['slap'])
@command_requires_balance
def slap(message):
    target = message.reply_to_message.from_user.first_name if message.reply_to_message else "someone"
    bot.reply_to(message, f"👋 {message.from_user.first_name} slapped {target}! 😆")

@bot.message_handler(commands=['quote'])
@command_requires_balance
def quote(message):
    quotes = [
        "🌟 Keep pushing forward!",
        "💪 Every setback is a setup for a comeback.",
        "🔥 Success starts with self-belief.",
        "🌈 Stay positive and work hard."
    ]
    bot.reply_to(message, random.choice(quotes))

@bot.message_handler(commands=['rules'])
@command_requires_balance
def rules(message):
    bot.reply_to(message, "📜 **Group Rules:**\n1️⃣ Be respectful\n2️⃣ No spam\n3️⃣ Follow admin instructions\n4️⃣ Avoid offensive language\n5️⃣ Have fun", parse_mode="Markdown")

# --- Welcome & Goodbye ---
WELCOME_IMAGE = "https://i.ibb.co/QjzpnFyL/Picsart-25-10-06-22-05-54-728.png"

@bot.message_handler(content_types=['new_chat_members'])
def welcome(message):
    group = message.chat.title
    for member in message.new_chat_members:
        text = (
            f"🎮 **Welcome to {group}!** 🎮\n\n"
            f"👋 Hello **{member.first_name}**, welcome to the King Rank community!\n"
            f"🆔 ID: `{member.id}`\n\n"
            "⚔️ Level up, follow the rules, and earn your King Rank title."
        )
        bot.send_photo(message.chat.id, WELCOME_IMAGE, caption=text, parse_mode="Markdown")

@bot.message_handler(content_types=['left_chat_member'])
def goodbye(message):
    user = message.left_chat_member
    bot.send_message(message.chat.id, f"👋 Goodbye {user.first_name}! Your throne awaits elsewhere. 👑")

print("✅ Cris King Rank Bot is running...")
bot.infinity_polling()
