import telebot;
from telebot import types


bot = telebot.TeleBot('7152516720:AAEnyntL7rzcav5v7TG5XcWXsZoRSjjiJjM')

@bot.message_handler(commands=['start'])
def startBot(message):
  first_mess = f"<b>{message.from_user.first_name} {message.from_user.last_name}</b>, привет!\nХочешь расскажу немного о нашей компании?"
  bot.send_message(message.chat.id, first_mess, parse_mode='html')

@bot.message_handler(func=lambda msg: True)
def echo_all(message):
    bot.send_message(message.chat.id, message.text)
bot.infinity_polling()