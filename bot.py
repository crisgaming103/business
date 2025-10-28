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

# --- Inline menu with Access Key ---
def send_inline_menu(user_id, username, name):
    if user_balance.get(user_id, 0) <= 0:
        return False

    # --- Message with Access Key info ---
    info_text = (
        "👑 **Welcome to Cris Tool Access System**\n"
        "━━━━━━━━━━━━━━━━━━━━━━━\n"
        "🎯 *Your verified King Rank credentials are below:*\n\n"
        f"👤 **Name:** {name}\n"
        f"💬 **Username:** @{username if username else 'N/A'}\n"
        f"🆔 **User ID:** `{user_id}`\n"
        f"🔑 **Access Key:** `{ACCESS_KEY}`\n\n"
        "📩 *Please keep your access key confidential.*\n"
        "👇 Tap the button below to open your **King Rank Portal.**"
    )

    target_url = "https://business-ten-lac.vercel.app/"
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("👑 King Rank Access", url=target_url))

    bot.send_message(user_id, info_text, parse_mode="Markdown", reply_markup=markup)
    return True

@bot.message_handler(commands=['menu'])
def menu(message):
    user = message.from_user
    if send_inline_menu(user.id, user.username, user.first_name):
        bot.reply_to(message, "✅ Menu sent! Check your private chat.")
    else:
        bot.reply_to(message, "❌ You have no balance.")

# --- Start & help ---
@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, f"👋 Hello {message.from_user.first_name}!\nI'm **Cris Bot**.\nUse /help to see commands.", parse_mode="Markdown")

@bot.message_handler(commands=['help'])
def help_cmd(message):
    text = (
        "🤖 **Cris Bot Commands**\n\n"
        "🛡 Moderation (Admins & Owner)\n"
        "/ban /unban /kick /mute /unmute /warn /unwarn\n"
        "💰 Balance:\n/balance /menu\n"
        "🧠 Utilities:\n/id /info /quote /rules\n"
        "🎉 Fun:\n/hug /slap"
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
    quotes = ["🌟 Keep pushing forward!", "💪 Every setback is a setup for a comeback.", "🔥 Success starts with self-belief.", "🌈 Stay positive and work hard."]
    bot.reply_to(message, random.choice(quotes))

@bot.message_handler(commands=['rules'])
def rules(message):
    bot.reply_to(message, "📜 **Rules:**\n1️⃣ Be respectful\n2️⃣ No spam\n3️⃣ Follow admin instructions\n4️⃣ Avoid offensive words\n5️⃣ Enjoy your stay", parse_mode="Markdown")

# --- Warnings, mute/ban/kick (unchanged from your code) ---
# [Your existing warn, unwarn, mute, unmute, kick, ban, unban handlers stay here]

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
        if custom_text:
            text = custom_text.format(name=name, username=username, id=user_id, group=group_name)
        else:
            text = (
                f"🎉 **Welcome to {group_name}!** 🎉\n\n"
                f"👋 Hello {name}, we are pleased to have you join our community.\n"
                f"💬 **Username:** {username}\n"
                f"🆔 **ID:** `{user_id}`\n\n"
                "📜 Please make sure to read /rules and follow them for a pleasant experience."
            )
        bot.send_photo(message.chat.id, WELCOME_IMAGE, caption=text, parse_mode="Markdown")

@bot.message_handler(content_types=['left_chat_member'])
def goodbye(message):
    user = message.left_chat_member
    group_name = message.chat.title
    text = (
        f"👋 **Goodbye, {user.first_name}!**\n\n"
        f"No one will miss you from **{group_name}** 😌\n"
        "We wish you the best in your future endeavors."
    )
    bot.send_photo(message.chat.id, GOODBYE_IMAGE, caption=text, parse_mode="Markdown")

print("✅ Cris Bot is running...")
bot.infinity_polling()
