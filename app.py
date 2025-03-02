import telebot
from config import curr, TOKEN
from extensions import APIException, CurrConverter

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start', 'help'])
def get_help(message: telebot.types.Message):
    bot.reply_to(message, '📚 Введите команду в формате:\n'
                          '<Валюта, цену которой хотите узнать> <Валюта, в которой узнать цену первой валюты> '
                          '<Количество первой валюты>\n'
                          'Например: доллар рубль 1\n'
                          'Список доступных валют: /values')

@bot.message_handler(commands=['values'])
def get_values(message: telebot.types.Message):
    text = '💰 Доступные валюты:'
    for i, k in enumerate(curr.keys()):
        text = '\n'.join((text, f'{i + 1}. {k.capitalize()}'))
    bot.reply_to(message, text)

@bot.message_handler(content_types=['text'])
def convert(message: telebot.types.Message):
    try:
        values = message.text.lower().strip().split()
        if len(values) != 3:
            raise APIException('Должно быть три передаваемых параметров!')

        quote, base, amount = values
        total_base = CurrConverter.get_price(quote, base, amount)
    except APIException as e:
        bot.reply_to(message, f'❌ Ошибка пользователя:\n{e}')
    except Exception as e:
        bot.reply_to(message, f'❌ Не удалось обработать команду:\n{e}')
    else:
        text = f'✅ Цена {amount} {curr[quote]} - {total_base} {curr[base]}'
        bot.reply_to(message, text)

bot.polling()