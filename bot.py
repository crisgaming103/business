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

# ─────────────── FILE SYSTEM ───────────────
if not os.path.exists(WELCOME_FILE):
    with open(WELCOME_FILE, "w") as f:
        json.dump({}, f, indent=4)

def load_welcome():
    with open(WELCOME_FILE, "r") as f:
        return json.load(f)

def save_welcome(data):
    with open(WELCOME_FILE, "w") as f:
        json.dump(data, f, indent=4)

# ─────────────── GLOBAL DATA ───────────────
user_balance = {}
user_warnings = {}

# ─────────────── ADMIN CHECK ───────────────
def is_admin_or_owner(chat_id, user_id):
    if user_id == OWNER_ID:
        return True
    try:
        admins = [admin.user.id for admin in bot.get_chat_administrators(chat_id)]
        return user_id in admins
    except:
        return False

# ─────────────── BALANCE SYSTEM ───────────────
def has_balance(user_id):
    return user_balance.get(user_id, 0) > 0 or user_balance.get(user_id) == float('inf')

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

# ─────────────── ACCESS MENU ───────────────
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
        "🔒 Please keep your access credentials confidential.\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━━\n"
        "🏆 **About King Rank**\n"
        "🔥 You’ve entered the elite circle of Cris players — the top-tier community of skill and dedication.\n"
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

@bot.message_handler(commands=['menu'])
def menu(message):
    user = message.from_user
    if send_inline_menu(user.id, user.username, user.first_name):
        bot.reply_to(message, "✅ Portal link sent! Check your private chat.")
    else:
        bot.reply_to(message, "❌ You have no balance or access.")

# ─────────────── START / HELP ───────────────
@bot.message_handler(commands=['start'])
def start(message):
    if not has_balance(message.from_user.id):
        return bot.reply_to(message, "🚫 **Access Denied**\nYou currently have **no balance**.\n💳 Contact the admin to recharge.", parse_mode="Markdown")
    bot.reply_to(message, f"👋 Welcome {message.from_user.first_name}!\nUse /menu to access your **King Rank Portal.**", parse_mode="Markdown")

@bot.message_handler(commands=['help'])
def help_cmd(message):
    text = (
        "🤖 **Cris King Rank Bot Commands**\n\n"
        "🛡 **Admin Tools**\n"
        "/warn /unwarn /mute /unmute /kick /ban /unban\n"
        "/quote /ping\n\n"
        "💰 **Balance System**\n"
        "/give /balance /menu\n\n"
        "🎯 **Info & Fun**\n"
        "/id /info /hug /slap /rules"
    )
    bot.reply_to(message, text, parse_mode="Markdown")

# ─────────────── UTILITY DECORATOR ───────────────
def command_requires_balance(func):
    def wrapper(message):
        if not has_balance(message.from_user.id) and message.from_user.id != OWNER_ID:
            return bot.reply_to(message, "🚫 You must have balance to use this command.")
        func(message)
    return wrapper

# ─────────────── INFO & FUN ───────────────
@bot.message_handler(commands=['id'])
@command_requires_balance
def get_id(message):
    bot.reply_to(message, f"🆔 Your ID: `{message.from_user.id}`", parse_mode="Markdown")

@bot.message_handler(commands=['quote'])
@command_requires_balance
def quote(message):
    quotes = [
        "🎯 Precision creates power.",
        "🔥 Every king was once a warrior.",
        "💪 Dominate. Don’t participate.",
        "🌟 Victory favors the focused."
    ]
    bot.reply_to(message, random.choice(quotes))

@bot.message_handler(commands=['ping'])
def ping(message):
    bot.reply_to(message, "🏓 Pong! The bot is online and ready.")

# ─────────────── ADMIN ACTION COMMANDS ───────────────
@bot.message_handler(commands=['warn'])
def warn_user(message):
    if not is_admin_or_owner(message.chat.id, message.from_user.id):
        return bot.reply_to(message, "🚫 Admins only.")
    if not message.reply_to_message:
        return bot.reply_to(message, "⚠️ Reply to a user to warn them.")
    user_id = message.reply_to_message.from_user.id
    user_warnings[user_id] = user_warnings.get(user_id, 0) + 1
    bot.reply_to(message, f"⚠️ {message.reply_to_message.from_user.first_name} has been warned ({user_warnings[user_id]}).")

@bot.message_handler(commands=['unwarn'])
def unwarn_user(message):
    if not is_admin_or_owner(message.chat.id, message.from_user.id):
        return bot.reply_to(message, "🚫 Admins only.")
    if not message.reply_to_message:
        return bot.reply_to(message, "⚠️ Reply to a user to remove warning.")
    user_id = message.reply_to_message.from_user.id
    user_warnings[user_id] = max(user_warnings.get(user_id, 1) - 1, 0)
    bot.reply_to(message, f"✅ Warning removed from {message.reply_to_message.from_user.first_name}.")

@bot.message_handler(commands=['kick'])
def kick_user(message):
    if not is_admin_or_owner(message.chat.id, message.from_user.id):
        return bot.reply_to(message, "🚫 Admins only.")
    if not message.reply_to_message:
        return bot.reply_to(message, "⚠️ Reply to the user to kick.")
    try:
        bot.ban_chat_member(message.chat.id, message.reply_to_message.from_user.id)
        bot.unban_chat_member(message.chat.id, message.reply_to_message.from_user.id)
        bot.reply_to(message, f"👢 {message.reply_to_message.from_user.first_name} was kicked out!")
    except Exception as e:
        bot.reply_to(message, f"❌ Error: {e}")

@bot.message_handler(commands=['ban'])
def ban_user(message):
    if not is_admin_or_owner(message.chat.id, message.from_user.id):
        return bot.reply_to(message, "🚫 Admins only.")
    if not message.reply_to_message:
        return bot.reply_to(message, "⚠️ Reply to the user to ban.")
    bot.ban_chat_member(message.chat.id, message.reply_to_message.from_user.id)
    bot.reply_to(message, f"🚫 {message.reply_to_message.from_user.first_name} has been banned.")

@bot.message_handler(commands=['unban'])
def unban_user(message):
    if not is_admin_or_owner(message.chat.id, message.from_user.id):
        return bot.reply_to(message, "🚫 Admins only.")
    args = message.text.split()
    if len(args) < 2:
        return bot.reply_to(message, "⚠️ Usage: /unban <user_id>")
    user_id = int(args[1])
    bot.unban_chat_member(message.chat.id, user_id)
    bot.reply_to(message, f"✅ User {user_id} has been unbanned.")

@bot.message_handler(commands=['mute'])
def mute_user(message):
    if not is_admin_or_owner(message.chat.id, message.from_user.id):
        return bot.reply_to(message, "🚫 Admins only.")
    if not message.reply_to_message:
        return bot.reply_to(message, "⚠️ Reply to the user to mute.")
    perms = ChatPermissions(can_send_messages=False)
    bot.restrict_chat_member(message.chat.id, message.reply_to_message.from_user.id, permissions=perms)
    bot.reply_to(message, f"🔇 {message.reply_to_message.from_user.first_name} has been muted.")

@bot.message_handler(commands=['unmute'])
def unmute_user(message):
    if not is_admin_or_owner(message.chat.id, message.from_user.id):
        return bot.reply_to(message, "🚫 Admins only.")
    if not message.reply_to_message:
        return bot.reply_to(message, "⚠️ Reply to the user to unmute.")
    perms = ChatPermissions(can_send_messages=True)
    bot.restrict_chat_member(message.chat.id, message.reply_to_message.from_user.id, permissions=perms)
    bot.reply_to(message, f"🔊 {message.reply_to_message.from_user.first_name} can now speak.")

# ─────────────── WELCOME & GOODBYE ───────────────
WELCOME_IMAGE = "https://i.ibb.co/QjzpnFyL/Picsart-25-10-06-22-05-54-728.png"

@bot.message_handler(content_types=['new_chat_members'])
def welcome(message):
    for member in message.new_chat_members:
        text = (
            f"🎮 **Welcome to {message.chat.title}!** 🎮\n\n"
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
