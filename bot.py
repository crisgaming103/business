import telebot
from telebot import types
import json
import os
import random
import threading
import time
import requests
import io

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
def start(message):
    user = message.from_user

    # Fancy Crisbot start text
    text = (
        f"────「 𝙲𝚁𝙸𝚂𝙱𝙾𝚃 」────\n"
        f"❂ ʜᴇʟʟ𝚘 {user.first_name}.{user.id}...\n"
        f"×⋆✦⋆──────────────⋆✦⋆×\n"
        f"ɪ ᴀᴍ 𝙲𝚛𝚒𝚜𝚋𝚘𝚝 ᴀ ɢʀᴏᴜᴘ ᴍᴀɴᴀɢᴇᴍᴇɴᴛ ᴡʜɪᴄʜ ᴄᴀɴ ʜᴇʟᴘ ʏᴏᴜ ᴛᴏ ᴍᴀɴᴀɢᴇ ᴀɴᴅ ꜱᴇᴄᴜʀᴇ ʏᴏᴜʀ ɢʀᴏᴜᴘ.\n"
        f"×⋆✦⋆──────────────⋆✦⋆×\n"
        f"ᴄʟɪᴄᴋ ᴏɴ /help ᴄᴏᴍᴍᴀɴᴅs ᴛᴏ ʟᴇᴀʀɴ ᴍᴏʀᴇ!"
    )

    # Inline button to add bot to a group
    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton(
            "➕ Add me to your group", 
            url=f"https://t.me/{bot.get_me().username}?startgroup=true"
        )
    )

    # Welcome image
    start_image = "https://i.ibb.co/Z7SvBv0/Picsart-25-10-29-09-31-06-902.jpg"

    # Send photo with caption and inline button
    bot.send_photo(
        chat_id=message.chat.id, 
        photo=start_image, 
        caption=text, 
        parse_mode="Markdown", 
        reply_markup=markup
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
        
    

@bot.message_handler(commands=['html'])
def ask_name(message):
    bot.reply_to(message, "🎂 Please enter the *name* of the celebrant:", parse_mode="Markdown")
    bot.register_next_step_handler(message, ask_birthdate)

def ask_birthdate(message):
    name = message.text.strip()
    msg = bot.reply_to(message, f"📅 Nice! Now enter the *birthdate* of {name} (format: YYYY-MM-DD):", parse_mode="Markdown")
    bot.register_next_step_handler(msg, ask_age, name)

def ask_age(message, name):
    birthdate = message.text.strip()
    msg = bot.reply_to(message, "🎈 Great! Enter the *age* of the celebrant:", parse_mode="Markdown")
    bot.register_next_step_handler(msg, ask_message, name, birthdate)

def ask_message(message, name, birthdate):
    age = message.text.strip()
    msg = bot.reply_to(message, "💌 Finally, enter your *birthday message* (what should appear on the gift card):", parse_mode="Markdown")
    bot.register_next_step_handler(msg, generate_html, name, birthdate, age)

def generate_html(message, name, birthdate, age):
    import io, datetime
    bday_message = message.text.strip()
    today = datetime.date.today().strftime("%Y-%m-%d")
    is_birthday = "🎉 TODAY is the special day!" if today == birthdate else "🎁 Countdown to the big day!"

    html_code = f"""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>🎂 Happy Birthday {name}!</title>
<style>
  body {{
    margin: 0;
    overflow: hidden;
    background: linear-gradient(135deg, #ff9a9e, #fad0c4);
    height: 100vh;
    display: flex;
    justify-content: center;
    align-items: center;
    font-family: 'Comic Sans MS', cursive;
  }}
  .card {{
    background: white;
    border-radius: 20px;
    box-shadow: 0 0 30px rgba(255, 105, 180, 0.5);
    padding: 40px;
    text-align: center;
    z-index: 2;
    position: relative;
  }}
  h1 {{
    color: #ff69b4;
    font-size: 3em;
  }}
  p {{
    font-size: 1.2em;
    color: #555;
  }}
  .balloon {{
    position: absolute;
    bottom: -150px;
    width: 60px;
    height: 80px;
    background: radial-gradient(circle at 30% 30%, #ffb6c1, #ff69b4);
    border-radius: 60% 60% 60% 60%;
    animation: float 6s ease-in-out infinite;
  }}
  .balloon::after {{
    content: '';
    position: absolute;
    width: 2px;
    height: 100px;
    background: #666;
    top: 80px;
    left: 50%;
    transform: translateX(-50%);
  }}
  @keyframes float {{
    0% {{ transform: translateY(0) rotate(0deg); opacity: 1; }}
    50% {{ transform: translateY(-300px) rotate(10deg); opacity: 0.9; }}
    100% {{ transform: translateY(-600px) rotate(-10deg); opacity: 0; }}
  }}
</style>
</head>
<body>
  <div class="card">
    <h1>🎂 Happy Birthday, {name}!</h1>
    <p>Age: <b>{age}</b></p>
    <p>Birthdate: <b>{birthdate}</b></p>
    <p>{is_birthday}</p>
    <hr style="margin:20px 0;">
    <h3>💌 Your Message:</h3>
    <p>{bday_message}</p>
    <h2>🎉 From CrisGaming Bot 💖</h2>
  </div>

  <!-- Floating Balloons -->
  <div class="balloon" style="left:10%; animation-delay:0s;"></div>
  <div class="balloon" style="left:30%; animation-delay:2s; background:radial-gradient(circle at 30% 30%, #ffe680, #ffcc00);"></div>
  <div class="balloon" style="left:50%; animation-delay:1s; background:radial-gradient(circle at 30% 30%, #b0e0e6, #00bfff);"></div>
  <div class="balloon" style="left:70%; animation-delay:3s; background:radial-gradient(circle at 30% 30%, #98fb98, #32cd32);"></div>
  <div class="balloon" style="left:90%; animation-delay:4s; background:radial-gradient(circle at 30% 30%, #dda0dd, #ba55d3);"></div>
</body>
</html>
"""

    file_obj = io.BytesIO(html_code.encode('utf-8'))
    file_obj.name = f"happy_birthday_{name.lower().replace(' ', '_')}.html"
    bot.send_document(
        chat_id=message.chat.id,
        document=file_obj,
        caption=f"🎁 Here’s your personalized birthday gift card for {name}! 🎉"
    )
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
        return bot.reply_to(message, "This command only works in groups.")
    
    if not message.reply_to_message:
        return bot.reply_to(message, "Reply to a user's message to mute them.")
    
    user_id = message.reply_to_message.from_user.id
    member = bot.get_chat_member(message.chat.id, message.from_user.id)
    
    if member.status not in ['administrator', 'creator']:
        return bot.reply_to(message, "Only admins can mute users.")
    
    until_date = int(time.time() + 3600)  # 1 hour in UTC timestamp
    
    bot.restrict_chat_member(
        chat_id=message.chat.id,
        user_id=user_id,
        permissions=types.ChatPermissions(can_send_messages=False),
        until_date=until_date
    )
    
    bot.reply_to(
        message,
        f"🔇 User [{user_id}](tg://user?id={user_id}) has been muted for 1 hour ⏳",
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
        "🎮 **Fun:** /hug /slap/html"
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
WELCOME_IMAGE = "https://i.ibb.co/Z7SvBv0/Picsart-25-10-29-09-31-06-902.jpg"
GOODBYE_IMAGE = "https://i.ibb.co/pjZjGBvp/Picsart-25-10-28-22-05-21-023.jpg"

import random
import random

@bot.message_handler(content_types=['new_chat_members'])
def welcome(message):
    group_name = message.chat.title

    for member in message.new_chat_members:
        username = f"@{member.username}" if member.username else "❌ None"

        # Professional welcome text
        text = (
            f"🌟 **Welcome to {group_name}!** 🌟\n\n"
            f"👋 Hello, **{member.first_name}**!\n"
            f"💬 Username : {username}\n"
            f"🆔 ID       : `{member.id}`\n\n"
            f"✨ We’re thrilled to have you here. Please check the /rules to get started.\n"
            f"🎮 Enjoy your time and participate actively!\n\n"
            f"📌 Group: **{group_name}**"
        )

        # Optionally, you can use a professional-looking welcome image
        bot.send_photo(
            chat_id=message.chat.id,
            photo=WELCOME_IMAGE,
            caption=text,
            parse_mode="Markdown"
        )
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
