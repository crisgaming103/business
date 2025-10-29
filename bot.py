import telebot
from telebot import types
import json
import os
import random
import threading
import time
import requests

BOT_TOKEN = "8210989428:AAEmQW5V1fsYTSLDQzxv6_KaiUX5ZLQOHLI"
bot = telebot.TeleBot(BOT_TOKEN)

WELCOME_FILE = "welcome_messages.json"
OWNER_ID = 6784382795
ACCESS_KEY = "Cris-rank-2025"

# ===================== #
#  AUTO DELETE SYSTEM   #
# ===================== #
AUTO_DELETE_DELAY = 1800  # 30 minutes (in seconds)

def auto_delete(chat_id, message_id):
    """Deletes a bot message silently after delay."""
    time.sleep(AUTO_DELETE_DELAY)
    try:
        bot.delete_message(chat_id, message_id)
    except:
        pass  # ignore errors (e.g., message already deleted)

def send_and_auto_delete(chat_id, *args, **kwargs):
    """Send message and schedule deletion if private chat."""
    msg = bot.send_message(chat_id, *args, **kwargs)
    try:
        chat = bot.get_chat(chat_id)
        if chat.type == "private":  # only delete private chat messages
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
#   BALANCE CHECK DECORATOR
# ===================== #
def require_balance(func):
    """Decorator to block commands if user has no balance."""
    def wrapper(message, *args, **kwargs):
        bal = user_balance.get(message.from_user.id, 0)
        if bal <= 0:
            send_and_auto_delete(message.chat.id, "❌ Access denied. You have no balance.")
            return
        return func(message, *args, **kwargs)
    return wrapper
@bot.message_handler(commands=['start'])

@require_balance
def start(message):
    send_and_auto_delete(
        message.chat.id,
        f"👋 Hello {message.from_user.first_name}!\n"
        "Welcome to **Cris Bot** — your King Rank assistant.\n"
        "Use /help to see commands.",
        parse_mode="Markdown"
    )

# ===================== #
#       MENU COMMAND
# ===================== #
@bot.message_handler(commands=['menu'])
@require_balance
def menu(message):
    user = message.from_user
    if send_inline_menu(user.id, user.username, user.first_name):
        send_and_auto_delete(message.chat.id, "✅ Menu sent! Check your private chat.")
    else:
        send_and_auto_delete(message.chat.id, "❌ You have no balance.")

# ===================== #
#     OTHER COMMANDS
# ===================== #
@bot.message_handler(commands=['balance'])
def check_balance(message):
    user = message.from_user
    bal = user_balance.get(user.id, 0)
    balance_text = "💎 Unlimited" if bal == float('inf') else f"💰 {bal:,}"  # adds commas for readability

    text = (
        "╔══════════════════════════╗\n"
        "       👑 CRIS TOOL 👑\n"
        "╚══════════════════════════╝\n\n"
        f"👋 Hello, *{user.first_name}*!\n"
        "✨ Welcome back to your [🇵🇭] Cris Game Dashboard.\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "📊 ACCOUNT STATUS\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"👤 Name       : *{user.first_name}*\n"
        f"🆔 ID         : `{user.id}`\n"
        f"🛡aBalance:{balance_text}\n"
        f"⚡ Status     : ✅ Access Confirmed\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "🔥 *CrisGame isn’t given, it’s taken.* 🔥\n"
        "💡 Keep your credentials safe and enjoy your VIP privileges!\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━"
    )

    send_and_auto_delete(message.chat.id, text, parse_mode="Markdown")

# ===================== #
#     BALANCE SYSTEM    #
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
#   ADMIN COMMANDS      #
# ===================== #
def extract_user(message):
    if message.reply_to_message:
        return message.reply_to_message.from_user
    args = message.text.split()
    if len(args) >= 2 and args[1].isdigit():
        return type('User', (), {'id': int(args[1]), 'first_name': f'User {args[1]}'})()
    return None

@bot.message_handler(commands=['kick'])
def kick_user(message):
    if not is_admin_or_owner(message.chat.id, message.from_user.id):
        return send_and_auto_delete(message.chat.id, "🚫 You don’t have permission.")
    target = extract_user(message)
    if not target:
        return send_and_auto_delete(message.chat.id, "⚠️ Reply or use /kick <user_id>")
    try:
        bot.kick_chat_member(message.chat.id, target.id)
        send_and_auto_delete(message.chat.id, f"👢 {target.first_name} has been kicked!")
    except:
        send_and_auto_delete(message.chat.id, "❌ Failed to kick user.")

@bot.message_handler(commands=['ban'])
def ban_user(message):
    if not is_admin_or_owner(message.chat.id, message.from_user.id):
        return send_and_auto_delete(message.chat.id, "🚫 You don’t have permission.")
    target = extract_user(message)
    if not target:
        return send_and_auto_delete(message.chat.id, "⚠️ Reply or use /ban <user_id>")
    try:
        bot.ban_chat_member(message.chat.id, target.id)
        send_and_auto_delete(message.chat.id, f"🔒 {target.first_name} has been banned!")
    except:
        send_and_auto_delete(message.chat.id, "❌ Failed to ban user.")

@bot.message_handler(commands=['unban'])
def unban_user(message):
    if not is_admin_or_owner(message.chat.id, message.from_user.id):
        return send_and_auto_delete(message.chat.id, "🚫 You don’t have permission.")
    args = message.text.split()
    if len(args) < 2 or not args[1].isdigit():
        return send_and_auto_delete(message.chat.id, "⚠️ Usage: /unban <user_id>")
    user_id = int(args[1])
    try:
        bot.unban_chat_member(message.chat.id, user_id)
        send_and_auto_delete(message.chat.id, f"✅ User `{user_id}` has been unbanned!", parse_mode="Markdown")
    except:
        send_and_auto_delete(message.chat.id, "❌ Failed to unban user.")

# ===================== #
#   WARN SYSTEM         #
# ===================== #
user_warnings = {}

@bot.message_handler(commands=['warn'])
def warn_user(message):
    if not is_admin_or_owner(message.chat.id, message.from_user.id):
        return send_and_auto_delete(message.chat.id, "🚫 You don’t have permission.")
    target = extract_user(message)
    if not target:
        return send_and_auto_delete(message.chat.id, "⚠️ Reply or use /warn <user_id>")
    user_warnings[target.id] = user_warnings.get(target.id, 0) + 1
    send_and_auto_delete(message.chat.id, f"⚠️ {target.first_name} has been warned ({user_warnings[target.id]} warnings).")
    if user_warnings[target.id] >= 3:
        bot.kick_chat_member(message.chat.id, target.id)
        bot.send_message(message.chat.id, f"🚨 {target.first_name} reached 3 warnings and was kicked.")
        
# 🔇 Mute Command 
@bot.message_handler(commands=['mute'])
def mute_user(message):
    if message.chat.type not in ['group', 'supergroup']:
        bot.reply_to(message, "This command only works in groups.")
        return

    if not message.reply_to_message:
        bot.reply_to(message, "Reply to a user's message to mute them.")
        return

    user_id = message.reply_to_message.from_user.id
    member = bot.get_chat_member(message.chat.id, message.from_user.id)

    # Check if admin
    if member.status not in ['administrator', 'creator']:
        bot.reply_to(message, "Only admins can mute users.")
        return

    # Mute duration = 1 hour
    mute_duration = timedelta(hours=1)
    until_date = datetime.now() + mute_duration

    # Restrict user from sending messages for 1 hour
    bot.restrict_chat_member(
        message.chat.id,
        user_id,
        permissions=ChatPermissions(can_send_messages=False),
        until_date=until_date
    )

    bot.reply_to(
        message,
        f"🔇 User [{user_id}](tg://user?id={user_id}) has been muted for **1 hour** ⏳",
        parse_mode="Markdown"
    )


# 🔊 Unmute Command
@bot.message_handler(commands=['unmute'])
def unmute_user(message):
    if message.chat.type not in ['group', 'supergroup']:
        bot.reply_to(message, "This command only works in groups.")
        return

    if not message.reply_to_message:
        bot.reply_to(message, "Reply to a user's message to unmute them.")
        return

    user_id = message.reply_to_message.from_user.id
    member = bot.get_chat_member(message.chat.id, message.from_user.id)

    # Check if admin
    if member.status not in ['administrator', 'creator']:
        bot.reply_to(message, "Only admins can unmute users.")
        return

    # Restore full permissions
    bot.restrict_chat_member(
        message.chat.id,
        user_id,
        permissions=ChatPermissions(
            can_send_messages=True,
            can_send_media_messages=True,
            can_send_other_messages=True,
            can_add_web_page_previews=True
        )
    )

    bot.reply_to(message, f"🔊 User [{user_id}](tg://user?id={user_id}) has been unmuted.", parse_mode="Markdown")

@bot.message_handler(commands=['unwarn'])
def unwarn_user(message):
    if not is_admin_or_owner(message.chat.id, message.from_user.id):
        return send_and_auto_delete(message.chat.id, "🚫 You don’t have permission.")
    target = extract_user(message)
    if not target:
        return send_and_auto_delete(message.chat.id, "⚠️ Reply or use /unwarn <user_id>")
    user_warnings[target.id] = max(0, user_warnings.get(target.id, 0) - 1)
    send_and_auto_delete(message.chat.id, f"✅ {target.first_name}'s warning removed ({user_warnings[target.id]} left).")

# ===================== #
#   BASIC COMMANDS      #
# ===================== #
@bot.message_handler(commands=['start'])
def start(message):
    send_and_auto_delete(message.chat.id, f"👋 Hello {message.from_user.first_name}!\nWelcome to **Cris Bot** — your King Rank assistant.\nUse /help to see commands.", parse_mode="Markdown")

@bot.message_handler(commands=['help'])
def help_cmd(message):
    text = (
        "🤖 **Cris Bot Command List**\n\n"
        "🛡 **Admin:** /kick /ban /unban /warn /unwarn/mute/unmute\n"
        "💰 **Balance:** /give /balance /menu\n"
        "🧠 **Info:** /id /info /rules /quote\n"
        "🎮 **Fun:** /hug /slap"
    )
    send_and_auto_delete(message.chat.id, text, parse_mode="Markdown")

@bot.message_handler(commands=['id'])
def get_id(message):
    send_and_auto_delete(message.chat.id, f"🆔 Your ID: `{message.from_user.id}`", parse_mode="Markdown")

@bot.message_handler(commands=['info'])
def info(message):
    # Determine target user
    target = message.reply_to_message.from_user if message.reply_to_message else message.from_user
    username = f"@{target.username}" if target.username else "❌ No username"
    
    # Get chat member info (to check rank)
    rank = "❌ Unknown"
    try:
        member = bot.get_chat_member(message.chat.id, target.id)
        status = member.status  # can be 'creator', 'administrator', 'member', 'restricted', 'left', 'kicked'
        if status == 'creator':
            rank = "👑 Owner"
        elif status == 'administrator':
            rank = "🛡️ Admin"
        elif status == 'member':
            rank = "👤 Member"
        elif status == 'restricted':
            rank = "⛔ Restricted"
        elif status == 'left':
            rank = "👋 Left"
        elif status == 'kicked':
            rank = "🚫 Banned"
        else:
            rank = f"ℹ️ {status}"
    except:
        rank = "❌ Unknown"

    # Profile link
    profile_link = f"[Link](tg://user?id={target.id})"

    # Send info message
    text = (
        f"👤 Name       : {target.first_name}\n"
        f"💬 Username   : {username}\n"
        f"🆔 Telegram ID: `{target.id}`\n"
        f"🏷️ Rank       : {rank}\n"
        f"🔗 Profile    : {profile_link}"
    )
    send_and_auto_delete(message.chat.id, text, parse_mode="Markdown")
    
# ===================== #
#   FUN COMMANDS        #
# ===================== #
@bot.message_handler(commands=['hug'])
def hug(message):
    target = message.reply_to_message.from_user.first_name if message.reply_to_message else "everyone"
    send_and_auto_delete(message.chat.id, f"🤗 {message.from_user.first_name} hugged {target}! 💞")

@bot.message_handler(commands=['slap'])
def slap(message):
    target = message.reply_to_message.from_user.first_name if message.reply_to_message else "someone"
    send_and_auto_delete(message.chat.id, f"👋 {message.from_user.first_name} slapped {target}! 😆")

@bot.message_handler(commands=['quote'])
def quote(message):
    quotes = [
        "🔥 Greatness begins with a single step.",
        "⚔️ Legends aren’t born, they’re made.",
        "🏆 Stay sharp, stay focused, stay king.",
        "🎮 Every loss is just training for your next win."
    ]
    send_and_auto_delete(message.chat.id, random.choice(quotes))

@bot.message_handler(commands=['rules'])
def rules(message):
    send_and_auto_delete(message.chat.id, "📜 **Rules:**\n1️⃣ Respect all\n2️⃣ No spam\n3️⃣ Follow admins\n4️⃣ No NSFW\n5️⃣ Enjoy your stay 👑", parse_mode="Markdown")

# ===================== #
#   WELCOME & GOODBYE   #
# ===================== #
WELCOME_IMAGE = "https://i.ibb.co/QjzpnFyL/Picsart-25-10-06-22-05-54-728.png"
GOODBYE_IMAGE = "https://i.ibb.co/QjzpnFyL/Picsart-25-10-06-22-05-54-728.png"

import random
import random

@bot.message_handler(content_types=['new_chat_members'])
def welcome(message):
    group_name = message.chat.title

    for member in message.new_chat_members:
        username = f"@{member.username}" if member.username else "❌ None"

        vibes = [
            f"🌞 **Welcome aboard, {member.first_name}!** Let’s spread some good vibes here in **{group_name}!** ✨",
            f"🎉 **Hey {member.first_name}!** The **{group_name}** family just got cooler 😎",
            f"🌈 **Big welcome, {member.first_name}!** Positive energy only in **{group_name}!** 💫",
            f"💖 **{member.first_name},** you’ve officially joined the good-vibes club — **{group_name}!** 🌟",
            f"🔥 **{member.first_name} has entered {group_name}!** Let’s level up the happiness 🚀",
            f"🌻 **Welcome, {member.first_name}!** May your stay in **{group_name}** be full of laughter and sunshine ☀️",
            f"✨ **{member.first_name},** we’re so glad you’re here in **{group_name}!** Let’s make great memories 🌈",
            f"🥳 **{member.first_name} joined {group_name}!** Good vibes only! 💕",
        ]

        vibe_message = random.choice(vibes)

        text = (
            f"{vibe_message}\n\n"
            f"💬 **Username:** {username}\n"
            f"🆔 `{member.id}`\n"
            f"🏷️ **Group:** {group_name}\n\n"
            "📘 Don’t forget to check /rules and enjoy your stay!"
        )

        bot.send_photo(message.chat.id, WELCOME_IMAGE, caption=text, parse_mode="Markdown")
import random

import random

@bot.message_handler(content_types=['left_chat_member'])
def goodbye(message):
    user = message.left_chat_member
    group_name = message.chat.title

    username = f"@{user.username}" if user.username else "❌ None"

    messages = [
        f"😤 **{user.first_name} left {group_name}!**\n\nFinally, less noise. 😒",
        f"👋 **Goodbye, {user.first_name}!**\n\nNobody’s gonna notice anyway 😏",
        f"💨 **{user.first_name} ran away from {group_name}.** Can’t handle the chaos 😂",
        f"🧹 **{user.first_name} disappeared!** The air feels cleaner already 😌",
        f"🚪 **{user.first_name} just left.** Don’t trip over the door on your way out 🤭",
        f"😈 **{user.first_name} left {group_name}.** Peace restored 🫡",
        f"👻 **{user.first_name} vanished.** The group feels lighter 😎",
        f"🕳️ **{user.first_name} is gone!** Maybe they’ll find a quieter place 🙄",
    ]

    text = (
        f"{random.choice(messages)}\n\n"
        f"💬 **Username:** {username}\n"
        f"🆔 `{user.id}`\n"
        f"🏷️ **Group:** {group_name}"
    )

    bot.send_photo(message.chat.id, GOODBYE_IMAGE, caption=text, parse_mode="Markdown")
    

# ===================== AUTO REACTION ===================== 
@bot.message_handler(func=lambda message: True, content_types=['text', 'sticker', 'photo', 'video'])
def auto_react(message):
    if message.from_user.id == bot.get_me().id:
        return

    reactions = [
        "👍", "👀", "🔥", "💯", "✨",
        "😂", "😎", "🤩", "🥳", "💖",
        "🙌", "👏", "😜", "😇", "😏",
        "🤔", "😱", "💪", "🎉", "💥",
        "😢", "😡", "😳", "🥶", "🤯",
        "💤", "🤗", "🤫", "😴", "💫",
        "🫶", "🫡", "🥰", "🫠", "💌",
        "🧿", "🌟", "🍀", "☄️", "💎"
    ]
    emoji = random.choice(reactions)

    # Use Bot API directly to react
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/setMessageReaction"
    data = {
        "chat_id": message.chat.id,
        "message_id": message.message_id,
        "reaction": emoji
    }
    try:
        requests.post(url, data=data)
    except Exception as e:
        print(f"Reaction failed: {e}")

# ===================== START BOT LOOP ===================== 
print("✅ Cris Bot is running...")
bot.infinity_polling()
