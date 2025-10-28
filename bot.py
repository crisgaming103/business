import telebot
from telebot import types
import json
import os
import random

BOT_TOKEN = "8210989428:AAEmQW5V1fsYTSLDQzxv6_KaiUX5ZLQOHLI"
bot = telebot.TeleBot(BOT_TOKEN)

WELCOME_FILE = "welcome_messages.json"
OWNER_ID = 6784382795  # Replace with your Telegram ID
ACCESS_KEY = "Cris-rank-2025"  # 🔑 Access key shown with the menu

# --- Load or create welcome JSON ---
if not os.path.exists(WELCOME_FILE):
    with open(WELCOME_FILE, "w") as f:
        json.dump({}, f, indent=4)

def load_welcome():
    with open(WELCOME_FILE, "r") as f:
        return json.load(f)

def save_welcome(data):
    with open(WELCOME_FILE, "w") as f:
        json.dump(data, f, indent=4)

# --- Admin check ---
def is_admin_or_owner(chat_id, user_id):
    if user_id == OWNER_ID:
        return True
    try:
        admins = [admin.user.id for admin in bot.get_chat_administrators(chat_id)]
        return user_id in admins
    except:
        return False

# --- Balance system ---
user_balance = {}

@bot.message_handler(commands=['give'])
def give_balance(message):
    if message.from_user.id != OWNER_ID:
        return bot.reply_to(message, "🚫 Only the owner can give balance.")
    if message.reply_to_message:
        target_user = message.reply_to_message.from_user
    else:
        args = message.text.split()
        if len(args) < 2 or not args[1].isdigit():
            return bot.reply_to(message, "⚠️ Usage: /give <user_id> or reply to a user")
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

# --- Inline menu with Access Key ---
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
    "🔒 Please keep your access credentials confidential at all times.\n\n"
    "━━━━━━━━━━━━━━━━━━━━━━━\n"
    "🏆 **About King Rank**\n"
    "🔥 You’ve entered the elite circle of Cris players — the top-tier community of strategy, skill, and dedication.\n"
    "Each rank milestone represents your achievements and commitment within the system.\n\n"
    "💠 *Your privileges include:*\n"
    "• Early access to upcoming features\n"
    "• Priority in-game tools and customization\n"
    "• Recognition among the King Rank elite\n\n"
    "🚀 Tap below to open your **King Rank Control Center** and begin your journey to dominance."
)

    target_url = "https://business-ten-lac.vercel.app/"
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("👑 Open King Rank Portal", url=target_url))

    bot.send_message(user_id, info_text, parse_mode="Markdown", reply_markup=markup)
    return True

@bot.message_handler(commands=['menu'])
def menu(message):
    user = message.from_user
    if send_inline_menu(user.id, user.username, user.first_name):
        bot.reply_to(message, "✅ Menu sent! Check your private chat.")
    else:
        bot.reply_to(message, "❌ You have no balance.")

# --- Admin Commands ---
def extract_user(message):
    """Extract user from reply or command argument."""
    if message.reply_to_message:
        return message.reply_to_message.from_user
    args = message.text.split()
    if len(args) >= 2 and args[1].isdigit():
        return type('User', (), {'id': int(args[1]), 'first_name': f'User {args[1]}'})()
    return None

@bot.message_handler(commands=['kick'])
def kick_user(message):
    if not is_admin_or_owner(message.chat.id, message.from_user.id):
        return bot.reply_to(message, "🚫 You don’t have permission.")
    target = extract_user(message)
    if not target:
        return bot.reply_to(message, "⚠️ Reply or use /kick <user_id>")
    try:
        bot.kick_chat_member(message.chat.id, target.id)
        bot.reply_to(message, f"👢 {target.first_name} has been kicked!")
    except:
        bot.reply_to(message, "❌ Failed to kick user.")

@bot.message_handler(commands=['ban'])
def ban_user(message):
    if not is_admin_or_owner(message.chat.id, message.from_user.id):
        return bot.reply_to(message, "🚫 You don’t have permission.")
    target = extract_user(message)
    if not target:
        return bot.reply_to(message, "⚠️ Reply or use /ban <user_id>")
    try:
        bot.ban_chat_member(message.chat.id, target.id)
        bot.reply_to(message, f"🔒 {target.first_name} has been banned!")
    except:
        bot.reply_to(message, "❌ Failed to ban user.")

@bot.message_handler(commands=['unban'])
def unban_user(message):
    if not is_admin_or_owner(message.chat.id, message.from_user.id):
        return bot.reply_to(message, "🚫 You don’t have permission.")
    args = message.text.split()
    if len(args) < 2 or not args[1].isdigit():
        return bot.reply_to(message, "⚠️ Usage: /unban <user_id>")
    user_id = int(args[1])
    try:
        bot.unban_chat_member(message.chat.id, user_id)
        bot.reply_to(message, f"✅ User `{user_id}` has been unbanned!", parse_mode="Markdown")
    except:
        bot.reply_to(message, "❌ Failed to unban user.")

# --- Warn system ---
user_warnings = {}

@bot.message_handler(commands=['warn'])
def warn_user(message):
    if not is_admin_or_owner(message.chat.id, message.from_user.id):
        return bot.reply_to(message, "🚫 You don’t have permission.")
    target = extract_user(message)
    if not target:
        return bot.reply_to(message, "⚠️ Reply or use /warn <user_id>")
    user_warnings[target.id] = user_warnings.get(target.id, 0) + 1
    bot.reply_to(message, f"⚠️ {target.first_name} has been warned ({user_warnings[target.id]} warnings).")
    if user_warnings[target.id] >= 3:
        bot.kick_chat_member(message.chat.id, target.id)
        bot.send_message(message.chat.id, f"🚨 {target.first_name} reached 3 warnings and was kicked.")

@bot.message_handler(commands=['unwarn'])
def unwarn_user(message):
    if not is_admin_or_owner(message.chat.id, message.from_user.id):
        return bot.reply_to(message, "🚫 You don’t have permission.")
    target = extract_user(message)
    if not target:
        return bot.reply_to(message, "⚠️ Reply or use /unwarn <user_id>")
    user_warnings[target.id] = max(0, user_warnings.get(target.id, 0) - 1)
    bot.reply_to(message, f"✅ {target.first_name}'s warning removed ({user_warnings[target.id]} left).")

# --- Start & help ---
@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, f"👋 Hello {message.from_user.first_name}!\nWelcome to **Cris Bot** — your professional King Rank assistant.\nUse /help to see available commands.", parse_mode="Markdown")

@bot.message_handler(commands=['help'])
def help_cmd(message):
    text = (
        "🤖 **Cris Bot Command List**\n\n"
        "🛡 **Admin Tools:**\n"
        "/kick /ban /unban /warn /unwarn\n\n"
        "💰 **Balance Commands:**\n"
        "/give /balance /menu\n\n"
        "🧠 **Utility Commands:**\n"
        "/id /info /rules /quote\n\n"
        "🎮 **Fun Commands:**\n"
        "/hug /slap"
    )
    bot.reply_to(message, text, parse_mode="Markdown")

# --- ID & info ---
@bot.message_handler(commands=['id'])
def get_id(message):
    bot.reply_to(message, f"🆔 Your ID: `{message.from_user.id}`", parse_mode="Markdown")

@bot.message_handler(commands=['info'])
def info(message):
    target = message.reply_to_message.from_user if message.reply_to_message else message.from_user
    username = f"@{target.username}" if target.username else "❌ No username"
    bot.reply_to(message, f"👤 Name: {target.first_name}\n💬 Username: {username}\n🆔 ID: `{target.id}`", parse_mode="Markdown")

# --- Fun commands ---
@bot.message_handler(commands=['hug'])
def hug(message):
    target = message.reply_to_message.from_user.first_name if message.reply_to_message else "everyone"
    bot.reply_to(message, f"🤗 {message.from_user.first_name} hugged {target}! 💞")

@bot.message_handler(commands=['slap'])
def slap(message):
    target = message.reply_to_message.from_user.first_name if message.reply_to_message else "someone"
    bot.reply_to(message, f"👋 {message.from_user.first_name} slapped {target}! 😆")

@bot.message_handler(commands=['quote'])
def quote(message):
    quotes = [
        "🔥 Greatness begins with a single step.",
        "⚔️ Legends aren’t born, they’re made.",
        "🏆 Stay sharp, stay focused, stay king.",
        "🎮 Every loss is just training for your next win."
    ]
    bot.reply_to(message, random.choice(quotes))

@bot.message_handler(commands=['rules'])
def rules(message):
    bot.reply_to(message, "📜 **Rules:**\n1️⃣ Respect all members\n2️⃣ No spam or toxicity\n3️⃣ Follow admin guidance\n4️⃣ No NSFW\n5️⃣ Enjoy your stay 👑", parse_mode="Markdown")

# --- Welcome & Goodbye ---
WELCOME_IMAGE = "https://i.ibb.co/QjzpnFyL/Picsart-25-10-06-22-05-54-728.png"
GOODBYE_IMAGE = "https://i.ibb.co/QjzpnFyL/Picsart-25-10-06-22-05-54-728.png"

@bot.message_handler(content_types=['new_chat_members'])
def welcome(message):
    data = load_welcome()
    chat_id = str(message.chat.id)
    custom_text = data.get(chat_id)
    group_name = message.chat.title
    for member in message.new_chat_members:
        name = member.first_name
        username = f"@{member.username}" if member.username else "❌ No username"
        user_id = member.id
        text = (
            f"🎉 **Welcome to {group_name}!** 🎉\n\n"
            f"👋 Hey {name}, we’re excited to have you join our squad.\n"
            f"💬 **Username:** {username}\n"
            f"🆔 **ID:** `{user_id}`\n\n"
            "📘 Read /rules before starting your journey. Let’s rise together! ⚔️"
        )
        bot.send_photo(message.chat.id, WELCOME_IMAGE, caption=text, parse_mode="Markdown")

@bot.message_handler(content_types=['left_chat_member'])
def goodbye(message):
    user = message.left_chat_member
    group_name = message.chat.title
    text = (
        f"👋 **Farewell, {user.first_name}!**\n\n"
        f"You’ve left **{group_name}**.\n"
        "We wish you success on your next mission. 🚀"
    )
    bot.send_photo(message.chat.id, GOODBYE_IMAGE, caption=text, parse_mode="Markdown")

print("✅ Cris Bot is running...")
bot.infinity_polling()
