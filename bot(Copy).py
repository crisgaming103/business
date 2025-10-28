import telebot
from telebot import types
import json
import os
import random
import requests

BOT_TOKEN = "8210989428:AAEmQW5V1fsYTSLDQzxv6_KaiUX5ZLQOHLI"
bot = telebot.TeleBot(BOT_TOKEN)

WELCOME_FILE = "welcome_messages.json"
OWNER_ID = 6784382795  # Replace with your Telegram ID

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

# --- Inline menu ---
def send_inline_menu(user_id):
    try:
        # Fetch user data from server
        response = requests.get(f"https://business-ten-lac.vercel.app/?user_id={user_id}", timeout=5)
        if response.status_code == 200:
            data = response.json()
            server_user_id = data.get("user_id")
            balance = data.get("balance", 0)

            # Only show menu if the user matches
            if server_user_id == user_id and balance > 0:
                markup = types.InlineKeyboardMarkup()
                markup.add(types.InlineKeyboardButton("👑 King rank", url="https://t.me/cpmkingrankbot"))
                bot.send_message(user_id,"✨ Tap the button below to access your rank:", reply_markup=markup, disable_web_page_preview=True)
                return True
    except:
        pass
    return False

@bot.message_handler(commands=['menu'])
def menu(message):
    if send_inline_menu(message.from_user.id):
        bot.reply_to(message,"✅ Menu sent! Check your private chat.")
    else:
        bot.reply_to(message,"❌ You have no balance or not registered on the server.")

# --- Balance system ---
@bot.message_handler(commands=['balance'])
def check_balance(message):
    user_id = message.from_user.id
    try:
        response = requests.get(f"http://king-rank1-2.vercel.app?user_id={user_id}", timeout=5)
        if response.status_code == 200:
            data = response.json()
            server_user_id = data.get("user_id")
            balance = data.get("balance", 0)

            if server_user_id == user_id:
                if balance == float('inf'):
                    bot.reply_to(message,"💰 You have unlimited balance!")
                else:
                    bot.reply_to(message,f"💰 Your balance: {balance}")
            else:
                bot.reply_to(message,"❌ No balance found for you.")
        else:
            bot.reply_to(message,"❌ Failed to fetch balance. Try again later.")
    except Exception as e:
        bot.reply_to(message,f"❌ Error fetching balance: {e}")

# --- Start & help ---
@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message,f"👋 Hello {message.from_user.first_name}!\nI'm **Cris Bot**.\nUse /help to see commands.", parse_mode="Markdown")

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
    bot.reply_to(message,text,parse_mode="Markdown")

# --- ID & info ---
@bot.message_handler(commands=['id'])
def get_id(message):
    bot.reply_to(message,f"🆔 Your ID: `{message.from_user.id}`",parse_mode="Markdown")

@bot.message_handler(commands=['info'])
def info(message):
    target = message.reply_to_message.from_user if message.reply_to_message else message.from_user
    username = f"@{target.username}" if target.username else "❌ No username"
    bot.reply_to(message,f"👤 Name: {target.first_name}\n💬 Username: {username}\n🆔 ID: `{target.id}`",parse_mode="Markdown")

# --- Fun commands ---
@bot.message_handler(commands=['hug'])
def hug(message):
    target = message.reply_to_message.from_user.first_name if message.reply_to_message else "everyone"
    bot.reply_to(message,f"🤗 {message.from_user.first_name} hugged {target}! 💞")

@bot.message_handler(commands=['slap'])
def slap(message):
    target = message.reply_to_message.from_user.first_name if message.reply_to_message else "someone"
    bot.reply_to(message,f"👋 {message.from_user.first_name} slapped {target}! 😆")

@bot.message_handler(commands=['quote'])
def quote(message):
    quotes = ["🌟 Keep pushing forward!","💪 Every setback is a setup for a comeback.","🔥 Success starts with self-belief.","🌈 Stay positive and work hard."]
    bot.reply_to(message,random.choice(quotes))

@bot.message_handler(commands=['rules'])
def rules(message):
    bot.reply_to(message,"📜 **Rules:**\n1️⃣ Be respectful\n2️⃣ No spam\n3️⃣ Follow admin instructions\n4️⃣ Avoid offensive words\n5️⃣ Enjoy your stay",parse_mode="Markdown")

# --- Warnings ---
warnings = {}
def get_target_user(message,index=1):
    if message.reply_to_message:
        return message.reply_to_message.from_user
    args = message.text.split()
    if len(args)>index and args[index].isdigit():
        return type('User',(),{'id':int(args[index]),'first_name':f'User {args[index]}'})()
    return None

@bot.message_handler(commands=['warn'])
def warn(message):
    if not is_admin_or_owner(message.chat.id,message.from_user.id):
        return bot.reply_to(message,"🚫 Only admins/owner")
    user = get_target_user(message)
    if not user:
        return bot.reply_to(message,"⚠️ Use reply or /warn <user_id>")
    warnings[user.id] = warnings.get(user.id,0)+1
    bot.reply_to(message,f"⚠️ {user.first_name} warned! Total: {warnings[user.id]}")

@bot.message_handler(commands=['unwarn'])
def unwarn(message):
    if not is_admin_or_owner(message.chat.id,message.from_user.id):
        return bot.reply_to(message,"🚫 Only admins/owner")
    user = get_target_user(message)
    if not user:
        return bot.reply_to(message,"⚠️ Use reply or /unwarn <user_id>")
    if user.id in warnings:
        warnings[user.id] = max(0,warnings[user.id]-1)
        bot.reply_to(message,f"✅ Removed one warning from {user.first_name}. Total: {warnings[user.id]}")
    else:
        bot.reply_to(message,f"ℹ️ {user.first_name} has no warnings")

# --- Mute/unmute ---
@bot.message_handler(commands=['mute'])
def mute(message):
    if not is_admin_or_owner(message.chat.id,message.from_user.id):
        return bot.reply_to(message,"🚫 Only admins/owner")
    user = get_target_user(message)
    if not user:
        return bot.reply_to(message,"⚠️ Use reply or /mute <user_id>")
    try:
        bot.restrict_chat_member(message.chat.id,user.id,can_send_messages=False)
        bot.reply_to(message,f"🔇 {user.first_name} muted")
    except Exception as e:
        bot.reply_to(message,f"❌ Error: {e}")

@bot.message_handler(commands=['unmute'])
def unmute(message):
    if not is_admin_or_owner(message.chat.id,message.from_user.id):
        return bot.reply_to(message,"🚫 Only admins/owner")
    user = get_target_user(message)
    if not user:
        return bot.reply_to(message,"⚠️ Use reply or /unmute <user_id>")
    try:
        bot.restrict_chat_member(message.chat.id,user.id,can_send_messages=True)
        bot.reply_to(message,f"🔊 {user.first_name} unmuted")
    except Exception as e:
        bot.reply_to(message,f"❌ Error: {e}")

# --- Kick/ban/unban ---
@bot.message_handler(commands=['kick'])
def kick(message):
    if not is_admin_or_owner(message.chat.id,message.from_user.id):
        return bot.reply_to(message,"🚫 Only admins/owner")
    user = get_target_user(message)
    if not user:
        return bot.reply_to(message,"⚠️ Use reply or /kick <user_id>")
    try:
        bot.kick_chat_member(message.chat.id,user.id)
        bot.unban_chat_member(message.chat.id,user.id)
        bot.reply_to(message,f"👢 {user.first_name} kicked")
    except Exception as e:
        bot.reply_to(message,f"❌ Error: {e}")

@bot.message_handler(commands=['ban'])
def ban(message):
    if not is_admin_or_owner(message.chat.id,message.from_user.id):
        return bot.reply_to(message,"🚫 Only admins/owner")
    user = get_target_user(message)
    if not user:
        return bot.reply_to(message,"⚠️ Use reply or /ban <user_id>")
    try:
        bot.ban_chat_member(message.chat.id,user.id)
        bot.reply_to(message,f"🚫 {user.first_name} banned")
    except Exception as e:
        bot.reply_to(message,f"❌ Error: {e}")

@bot.message_handler(commands=['unban'])
def unban(message):
    if not is_admin_or_owner(message.chat.id,message.from_user.id):
        return bot.reply_to(message,"🚫 Only admins/owner")
    user = get_target_user(message)
    if not user:
        return bot.reply_to(message,"⚠️ Use reply or /unban <user_id>")
    try:
        bot.unban_chat_member(message.chat.id,user.id)
        bot.reply_to(message,f"✅ {user.first_name} unbanned")
    except Exception as e:
        bot.reply_to(message,f"❌ Error: {e}")

# --- Welcome / Goodbye ---
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
