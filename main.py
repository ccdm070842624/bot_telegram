import telebot
bot = telebot.TeleBot('6924576400:AAG5OfZ39r6kLYXsC1Ud60ax3bTN9lZVpzs')

@bot.message.handler(commands=['start'])
def main(message):
  bot.send_message(message.chat.id, 'Hello')


bot.polling(non_stop=True)
