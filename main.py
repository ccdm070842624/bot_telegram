import telebot
bot = telebot.TeleBot('7036229459:AAGSdT9O3DPrv0lv4L5mDSAhu0nvMDqMuk0')

@bot.message.handler(commands=['start'])
def main(message):
  bot.send_message(message.chat.id, 'Hello')


bot.polling(non_stop=True)
