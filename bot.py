import telebot
from telebot import types
import json
import os
import random
import threading
import time
import requests
import io
import openai
from io import BytesIO

BOT_TOKEN = "8210989428:AAEmQW5V1fsYTSLDQzxv6_KaiUX5ZLQOHLI"
bot = telebot.TeleBot(BOT_TOKEN)
OPENAI_API_KEY = "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"
openai.api_key = OPENAI_API_KEY

WELCOME_FILE = "welcome_messages.json"
OWNER_ID = 6784382795
ACCESS_KEY = "Cris-rank-2025"

# ===================== #
#  AUTO DELETE SYSTEM   #
# ===================== #
AUTO_DELETE_DELAY = 1800  # 30 minutes

def auto_delete(chat_id, message_id):
    time.sleep(AUTO_DELETE_DELAY)
    try:
        bot.delete_message(chat_id, message_id)
    except:
        pass

def send_and_auto_delete(chat_id, *args, **kwargs):
    msg = bot.send_message(chat_id, *args, **kwargs)
    try:
        chat = bot.get_chat(chat_id)
        if chat.type == "private":
            threading.Thread(target=auto_delete, args=(chat_id, msg.message_id), daemon=True).start()
    except:
        pass
    return msg

# ===================== #
#   WELCOME FILE LOAD   #
# ===================== #
if not os.path.exists(WELCOME_FILE):
    with open(WELCOME_FILE, "w") as f:
        json.dump({}, f, indent=4)

def load_welcome():
    with open(WELCOME_FILE, "r") as f:
        return json.load(f)

def save_welcome(data):
    with open(WELCOME_FILE, "w") as f:
        json.dump(data, f, indent=4)

# ===================== #
#     ADMIN CHECK       #
# ===================== #
def is_admin_or_owner(chat_id, user_id):
    if user_id == OWNER_ID:
        return True
    try:
        admins = [admin.user.id for admin in bot.get_chat_administrators(chat_id)]
        return user_id in admins
    except:
        return False

# ===================== #
#   BALANCE SYSTEM      #
# ===================== #
user_balance = {}

@bot.message_handler(commands=['give'])
def give_balance(message):
    if message.from_user.id != OWNER_ID:
        return send_and_auto_delete(message.chat.id, "🚫 Only the owner can give balance.")
    if message.reply_to_message:
        target_user = message.reply_to_message.from_user
    else:
        args = message.text.split()
        if len(args) < 2 or not args[1].isdigit():
            return send_and_auto_delete(message.chat.id, "⚠️ Usage: /give <user_id> or reply to a user")
        target_user = type('User', (), {'id': int(args[1]), 'first_name': f'User {args[1]}'})()
    user_balance[target_user.id] = float('inf')
    send_and_auto_delete(message.chat.id, f"✅ {target_user.first_name} now has unlimited balance!")

@bot.message_handler(commands=['balance'])
def check_balance(message):
    bal = user_balance.get(message.from_user.id, 0)
    if bal == float('inf'):
        send_and_auto_delete(message.chat.id, "💰 You have unlimited balance!")
    else:
        send_and_auto_delete(message.chat.id, f"💰 Your balance: {bal}")

# ===================== #
#       START/HELP      #
# ===================== #
@bot.message_handler(commands=['start'])
def start(message):
    user = message.from_user
    text = (
        f"────「 𝙲𝚁𝙸𝚂𝙱𝙾𝚃 」────\n"
        f"❂ ʜᴇʟʟ𝚘 {user.first_name}.{user.id}...\n"
        f"×⋆✦⋆──────────────⋆✦⋆×\n"
        f"ɪ ᴀᴍ 𝙲𝚛𝚒𝚜𝙱𝙾𝚃, ᴀ ɢʀᴏᴜᴘ ᴍᴀɴᴀɢᴇᴍᴇɴᴛ ʙᴏᴛ.\n"
        f"×⋆✦⋆──────────────⋆✦⋆×\n"
        f"ᴄʟɪᴄᴋ /help ᴛᴏ ʟᴇᴀʀɴ ᴍᴏʀᴇ!"
    )
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("➕ Add me to your group", url=f"https://t.me/{bot.get_me().username}?startgroup=true"))
    bot.send_photo(chat_id=message.chat.id, photo="https://i.ibb.co/Z7SvBv0/Picsart-25-10-29-09-31-06-902.jpg", caption=text, parse_mode="Markdown", reply_markup=markup)

@bot.message_handler(commands=['help'])
def help_cmd(message):
    text = (
        "🤖 **CrisBot Command List**\n\n"
        "🛡 **Admin:** /kick /ban /unban /warn /unwarn /mute /unmute\n"
        "💰 **Balance:** /give /balance /menu\n"
        "🧠 **Info:** /id /info /rules /quote\n"
        "🎮 **Fun:** /hug /slap /html\n"
        "🤖 **AI:** /ask /logo /ai"
    )
    send_and_auto_delete(message.chat.id, text, parse_mode="Markdown")

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

@bot.message_handler(commands=['menu'])
def menu(message):
    user = message.from_user
    if send_inline_menu(user.id, user.username, user.first_name):
        send_and_auto_delete(message.chat.id, "✅ Menu sent! Check your private chat.")
    else:
        send_and_auto_delete(message.chat.id, "❌ You have no balance.")

# ===================== #
#      AI COMMANDS      #
# ===================== #
@bot.message_handler(commands=['ask'])
def ask_openai(message):
    msg = bot.send_message(message.chat.id, "📝 Send me your question for ChatGPT:")
    bot.register_next_step_handler(msg, ask_openai_step)

def ask_openai_step(message):
    user_question = message.text
    bot.send_chat_action(message.chat.id, 'typing')
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a helpful Telegram assistant."},
                {"role": "user", "content": user_question}
            ],
            temperature=0.7,
            max_tokens=500
        )
        answer = response['choices'][0]['message']['content']
        send_and_auto_delete(message.chat.id, f"💡 ChatGPT says:\n\n{answer}")
    except Exception as e:
        send_and_auto_delete(message.chat.id, f"❌ Error: {e}")

@bot.message_handler(commands=['logo'])
def generate_logo_cmd(message):
    msg = bot.send_message(message.chat.id, "✏️ Send me a description for your logo:")
    bot.register_next_step_handler(msg, generate_logo_step)

def generate_logo_step(message):
    prompt = message.text
    bot.send_chat_action(message.chat.id, 'typing')
    try:
        response = openai.Image.create(prompt=prompt, n=1, size="512x512")
        image_url = response['data'][0]['url']
        image_response = requests.get(image_url)
        bot.send_photo(message.chat.id, photo=image_response.content, caption=f"Here’s your logo for: {prompt}")
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Error generating logo: {e}")

# ===================== #
#  AUTO AI RESPONDER 🤖
# ===================== #
@bot.message_handler(func=lambda message: True, content_types=['text'])
def auto_ai_reply(message):
    # Ignore if message starts with a command
    if message.text.startswith("/"):
        return

    user_text = message.text.strip()
    if not user_text:
        return

    bot.send_chat_action(message.chat.id, 'typing')

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are CrisBot AI, a friendly assistant that chats naturally."},
                {"role": "user", "content": user_text}
            ],
            temperature=0.8,
            max_tokens=500
        )
        ai_reply = response['choices'][0]['message']['content']
        send_and_auto_delete(message.chat.id, ai_reply)
    except Exception as e:
        bot.send_message(message.chat.id, f"⚠️ AI error: {e}")

# ===================== #
#  MESSAGE MANAGEMENT   #
# ===================== #
@bot.message_handler(content_types=['new_chat_members'])
def welcome_new_member(message):
    for member in message.new_chat_members:
        bot.reply_to(message, f"🎉 Welcome, {member.first_name}! Enjoy your stay in {message.chat.title}!")

@bot.message_handler(content_types=['left_chat_member'])
def farewell_member(message):
    bot.reply_to(message, f"👋 {message.left_chat_member.first_name} has left the group.")

@bot.edited_message_handler(func=lambda message: True)
def edited_message(message):
    bot.reply_to(message, f"✏️ {message.from_user.first_name} edited a message:\n\n{message.text}")

@bot.message_handler(content_types=['forward_from', 'forward_from_chat'])
def forwarded_message(message):
    bot.reply_to(message, "📩 You forwarded a message!")

@bot.message_handler(content_types=['photo', 'video', 'document', 'audio', 'voice'])
def handle_media(message):
    bot.reply_to(message, f"📁 Received {message.content_type} from {message.from_user.first_name}.")

# ===================== #
#      BOT POLLING      #
# ===================== #
print("🤖 CrisBot with Auto AI + Message Manager is running...")
bot.infinity_polling()
