import telebot
import os
import json

TOKEN = 'YOUR_TELEGRAM_BOT_TOKEN'
AUTHORIZED_USER = 'authorized_user_username'
FILES_JSON = 'files.json'
bot = telebot.TeleBot(TOKEN)

def load_files():
    try:
        with open(FILES_JSON, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return {'files': []}

def save_files(data):
    with open(FILES_JSON, 'w') as file:
        json.dump(data, file, indent=2)

def stop_command(filenames, chat_id):
    data = load_files()

    for filename in filenames:
        for file in data['files']:
            if file['name'] == filename and file['status'] == 'running':
                os.system(f'pkill -f {filename}')
                file['status'] = 'stopped'
                bot.send_message(chat_id, f"File stopped: {filename}.")

    save_files(data)

def start_command(filenames, chat_id):
    data = load_files()

    for filename in filenames:
        for file in data['files']:
            if file['name'] == filename and file['status'] == 'stopped':
                os.system(f'python {filename} &')
                file['status'] = 'running'
                bot.send_message(chat_id, f"File started: {filename}.")

    save_files(data)

def add_files(filenames, chat_id):
    data = load_files()

    for filename in filenames:
        if not any(file['name'] == filename for file in data['files']):
            data['files'].append({"name": filename, "status": "stopped"})
            bot.send_message(chat_id, f"File added: {filename}.")

    save_files(data)

def remove_files(filenames, chat_id):
    data = load_files()

    for filename in filenames:
        data['files'] = [file for file in data['files'] if file['name'] != filename]
        bot.send_message(chat_id, f"File removed: {filename}.")

    save_files(data)

def help_command(chat_id):
    help_message = (
        "Available commands:\n"
        "/+ <file_name>: Start a file\n"
        "/- <file_name>: Stop a file\n"
        "/add <file_name>: Add a file\n"
        "/remove <file_name>: Remove a file\n"
        "/help: Show this help message"
    )
    bot.send_message(chat_id, help_message)

@bot.message_handler(func=lambda message: message.from_user.username == AUTHORIZED_USER)
def handle_authorized_user(message):
    command, *args = message.text.split()

    if command == '+':
        start_command(args, message.chat.id)
    elif command == '-':
        stop_command(args, message.chat.id)
    elif command == 'add':
        add_files(args, message.chat.id)
    elif command == 'remove':
        remove_files(args, message.chat.id)
    elif command == 'help':
        help_command(message.chat.id)
    else:
        bot.reply_to(message, "Command not understood.")

while True:
    try:
        bot.polling(none_stop=True)
    except Exception as e:
        print(f"An error occurred: {e}")
        # Handle exceptions (e.g., reconnect, log the error, etc.)
