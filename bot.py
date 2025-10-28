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
    if user_balance.get(user_id, 0) <= 0:
        return False

    info_text = (
        "🎮 **Welcome to Cris King Rank Portal** 🎮\n"
        "━━━━━━━━━━━━━━━━━━━━━━━\n"
        "🏆 *Elite Access Credentials:*\n\n"
        f"👤 **Name:** {name}\n"
        f"💬 **Username:** @{username if username else 'N/A'}\n"
        f"🆔 **User ID:** `{user_id}`\n"
        f"🔑 **Access Key:** `{ACCESS_KEY}`\n\n"
        "⚔️ *This key grants you exclusive access to the King Rank portal.*\n"
        "🔒 Keep your credentials private.\n\n"
        "👇 Tap below to enter your **King Rank Control Center.**"
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

# --- Info & Utility Commands ---
@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, f"👋 Hello {message.from_user.first_name}!\nWelcome to **Cris King Rank Bot.**\nUse /help to view available commands.", parse_mode="Markdown")

@bot.message_handler(commands=['help'])
def help_cmd(message):
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

@bot.message_handler(commands=['id'])
def get_id(message):
    bot.reply_to(message, f"🆔 Your ID: `{message.from_user.id}`", parse_mode="Markdown")

@bot.message_handler(commands=['info'])
def info(message):
    target = message.reply_to_message.from_user if message.reply_to_message else message.from_user
    username = f"@{target.username}" if target.username else "❌ No username"
    bot.reply_to(message, f"👤 Name: {target.first_name}\n💬 Username: {username}\n🆔 ID: `{target.id}`", parse_mode="Markdown")

# --- Fun Commands ---
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
        "🌟 Keep pushing forward!",
        "💪 Every setback is a setup for a comeback.",
        "🔥 Success starts with self-belief.",
        "🌈 Stay positive and work hard."
    ]
    bot.reply_to(message, random.choice(quotes))

@bot.message_handler(commands=['rules'])
def rules(message):
    bot.reply_to(message, "📜 **Group Rules:**\n1️⃣ Be respectful\n2️⃣ No spam\n3️⃣ Follow admin instructions\n4️⃣ Avoid offensive language\n5️⃣ Have fun", parse_mode="Markdown")

# --- Target Extraction ---
def extract_user(message):
    if message.reply_to_message:
        return message.reply_to_message.from_user
    parts = message.text.split()
    if len(parts) > 1 and parts[1].isdigit():
        try:
            return bot.get_chat_member(message.chat.id, int(parts[1])).user
        except:
            return None
    return None

# --- Moderation Commands ---
@bot.message_handler(commands=['warn'])
def warn_user(message):
    if not is_admin_or_owner(message.chat.id, message.from_user.id):
        return bot.reply_to(message, "🚫 You lack admin permissions.")
    target = extract_user(message)
    if not target:
        return bot.reply_to(message, "⚠️ Reply to a user or use `/warn <user_id>`", parse_mode="Markdown")
    user_warnings[target.id] = user_warnings.get(target.id, 0) + 1
    warns = user_warnings[target.id]
    bot.reply_to(message, f"⚠️ {target.first_name} has been warned ({warns}/5).")
    if warns == 3:
        bot.restrict_chat_member(message.chat.id, target.id, until_date=message.date + 600, permissions=ChatPermissions(can_send_messages=False))
        bot.send_message(message.chat.id, f"🔇 {target.first_name} muted for 10 minutes (3 warnings).")
    elif warns >= 5:
        try:
            bot.kick_chat_member(message.chat.id, target.id)
            bot.send_message(message.chat.id, f"⚔️ {target.first_name} was kicked after 5 warnings.")
        except:
            bot.send_message(message.chat.id, f"❌ Failed to kick {target.first_name} (missing permissions).")

@bot.message_handler(commands=['unwarn'])
def unwarn_user(message):
    if not is_admin_or_owner(message.chat.id, message.from_user.id):
        return bot.reply_to(message, "🚫 You lack admin permissions.")
    target = extract_user(message)
    if not target:
        return bot.reply_to(message, "⚠️ Reply or use `/unwarn <user_id>`", parse_mode="Markdown")
    if user_warnings.get(target.id, 0) > 0:
        user_warnings[target.id] -= 1
        bot.reply_to(message, f"✅ Removed one warning from {target.first_name}. ({user_warnings[target.id]}/5)")
    else:
        bot.reply_to(message, f"ℹ️ {target.first_name} has no warnings.")

@bot.message_handler(commands=['mute'])
def mute_user(message):
    if not is_admin_or_owner(message.chat.id, message.from_user.id):
        return bot.reply_to(message, "🚫 You lack admin permissions.")
    target = extract_user(message)
    if not target:
        return bot.reply_to(message, "⚠️ Reply or use `/mute <user_id> <minutes>`", parse_mode="Markdown")
    args = message.text.split()
    mute_time = int(args[2]) if len(args) > 2 and args[2].isdigit() else 5
    until_date = message.date + (mute_time * 60)
    try:
        bot.restrict_chat_member(message.chat.id, target.id, until_date=until_date, permissions=ChatPermissions(can_send_messages=False))
        bot.reply_to(message, f"🔇 {target.first_name} muted for {mute_time} minutes.")
    except Exception as e:
        bot.reply_to(message, f"❌ Failed to mute user.\nError: {e}")

@bot.message_handler(commands=['unmute'])
def unmute_user(message):
    if not is_admin_or_owner(message.chat.id, message.from_user.id):
        return bot.reply_to(message, "🚫 You lack admin permissions.")
    target = extract_user(message)
    if not target:
        return bot.reply_to(message, "⚠️ Reply or use `/unmute <user_id>`", parse_mode="Markdown")
    try:
        bot.restrict_chat_member(message.chat.id, target.id, permissions=ChatPermissions(can_send_messages=True))
        bot.reply_to(message, f"🔊 {target.first_name} has been unmuted.")
    except Exception as e:
        bot.reply_to(message, f"❌ Failed to unmute user.\nError: {e}")

@bot.message_handler(commands=['kick'])
def kick_user(message):
    if not is_admin_or_owner(message.chat.id, message.from_user.id):
        return bot.reply_to(message, "🚫 You lack admin permissions.")
    target = extract_user(message)
    if not target:
        return bot.reply_to(message, "⚠️ Reply or use `/kick <user_id>`", parse_mode="Markdown")
    try:
        bot.kick_chat_member(message.chat.id, target.id)
        bot.reply_to(message, f"👢 {target.first_name} was kicked.")
    except Exception as e:
        bot.reply_to(message, f"❌ Failed to kick user.\nError: {e}")

@bot.message_handler(commands=['ban'])
def ban_user(message):
    if not is_admin_or_owner(message.chat.id, message.from_user.id):
        return bot.reply_to(message, "🚫 You lack admin permissions.")
    target = extract_user(message)
    if not target:
        return bot.reply_to(message, "⚠️ Reply or use `/ban <user_id>`", parse_mode="Markdown")
    try:
        bot.ban_chat_member(message.chat.id, target.id)
        bot.reply_to(message, f"🔒 {target.first_name} permanently banned.")
    except Exception as e:
        bot.reply_to(message, f"❌ Failed to ban user.\nError: {e}")

@bot.message_handler(commands=['unban'])
def unban_user(message):
    if not is_admin_or_owner(message.chat.id, message.from_user.id):
        return bot.reply_to(message, "🚫 You lack admin permissions.")
    args = message.text.split()
    if len(args) < 2 or not args[1].isdigit():
        return bot.reply_to(message, "⚠️ Use `/unban <user_id>`", parse_mode="Markdown")
    try:
        bot.unban_chat_member(message.chat.id, int(args[1]))
        bot.reply_to(message, f"✅ User {args[1]} unbanned successfully.")
    except Exception as e:
        bot.reply_to(message, f"❌ Failed to unban user.\nError: {e}")

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
