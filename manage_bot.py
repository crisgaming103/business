import telebot
from telebot import types
import json
import threading
import time

BOT_TOKEN = "8301200241:AAGiD7VZx5XvSED1YmVBlUjiGddZXGBHNFc"
bot = telebot.TeleBot(BOT_TOKEN)

OWNER_ID = 6784382795
POST_FILE = "owner_post.json"
GROUP_LOG_FILE = "group_log.json"

# ===================== #
#     POST MANAGEMENT   #
# ===================== #

def load_post():
    try:
        with open(POST_FILE, "r") as f:
            return json.load(f)
    except:
        return {}

def save_post(post_data):
    with open(POST_FILE, "w") as f:
        json.dump(post_data, f)

# Set post (owner only)
@bot.message_handler(commands=["set_post"])
def set_post(message):
    if message.from_user.id != OWNER_ID:
        bot.reply_to(message, "❌ Only owner can set the post.")
        return
    post_content = message.text[len("/set_post "):].strip()
    if not post_content:
        bot.reply_to(message, "❌ Usage: /set_post Your message here")
        return
    save_post({"text": post_content})
    bot.reply_to(message, "✅ Post saved successfully.")

# Delete post (owner only)
@bot.message_handler(commands=["delete_post"])
def delete_post(message):
    if message.from_user.id != OWNER_ID:
        bot.reply_to(message, "❌ Only owner can delete the post.")
        return
    save_post({})
    bot.reply_to(message, "✅ Post deleted successfully.")

# Send post (any user in group can trigger)
@bot.message_handler(commands=["get_post"])
def get_post(message):
    post = load_post()
    if not post.get("text"):
        bot.reply_to(message, "❌ No post has been set by the owner.")
        return
    bot.send_message(message.chat.id, f"📢 Post:\n\n{post['text']}")

# ===================== #
#   GROUP AUTO DETECT   #
# ===================== #

def load_group_log():
    try:
        with open(GROUP_LOG_FILE, "r") as f:
            return json.load(f)
    except:
        return []

def save_group_log(log_data):
    with open(GROUP_LOG_FILE, "w") as f:
        json.dump(log_data, f)

@bot.message_handler(content_types=["new_chat_members"])
def detect_new_group(message):
    for member in message.new_chat_members:
        if member.id == bot.get_me().id:
            # Bot added to a new group
            group_info = {
                "group_id": message.chat.id,
                "group_name": message.chat.title,
                "added_by": message.from_user.username if message.from_user else "Unknown"
            }
            log = load_group_log()
            log.append(group_info)
            save_group_log(log)
            # Notify owner in private
            try:
                bot.send_message(OWNER_ID, f"✅ Bot added to new group:\nName: {group_info['group_name']}\nID: {group_info['group_id']}\nAdded by: {group_info['added_by']}")
            except:
                pass

# ===================== #
#       START BOT       #
# ===================== #
bot.infinity_polling()
