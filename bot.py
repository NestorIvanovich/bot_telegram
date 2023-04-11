import telebot
from config import TOKEN, currency_dict
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup
bot = telebot.TeleBot(TOKEN)
selected_currency = {}



@bot.message_handler(commands=['start',])
def start(message: telebot.types.Message):
    text = 'Привет! Я бот для конвертации валют.'
    keyboard = InlineKeyboardMarkup(row_width=3)
    btn1 = InlineKeyboardButton('начать', callback_data='begin')
    btn2 = InlineKeyboardButton('помощь', callback_data='help')
    btn3 = InlineKeyboardButton('доступные валюты', callback_data='values')
    keyboard.add(btn1)
    keyboard.add(btn2)
    keyboard.add(btn3)
    bot.send_message(message.chat.id, text, reply_markup=keyboard)


@bot.message_handler(commands=['values'])
def values_command(message: telebot.types.Message):
    values(message)

@bot.callback_query_handler(func=lambda call: call.data == 'values')
def values_callback(call):
    values(call.message)

def values(message: telebot.types.Message):
    answer = 'Доступные валюты:\n'
    for code, name in currency_dict.items():
        answer += f'{code} - {name}\n'
    bot.reply_to(message, answer)

@bot.message_handler(commands=['begin'])
def begin_command(message: telebot.types.Message):
    begin(message)

@bot.callback_query_handler(func=lambda call: call.data == 'begin')
def begin_callback(call):
    begin(call.message)

def begin(message):
    keyboard = InlineKeyboardMarkup()
    for i in currency_dict.keys():
        btn = telebot.types.InlineKeyboardButton(i, callback_data=f'{i} start')
        keyboard.add(btn)
    bot.send_message(chat_id=message.chat.id, text='Выберите начальную валюту:'
                     , reply_markup=keyboard)

@bot.callback_query_handler(func=lambda call: call.data[-5:] == 'start')
def get_start_currency(call):
    print(call.data, 1)
    selected_currency["from"] = call.data[:-6]
    keyboard = InlineKeyboardMarkup()
    for i in currency_dict.keys():
        if i != selected_currency['from']:
            btn = telebot.types.InlineKeyboardButton(i, callback_data=f'{i} finish')
            keyboard.add(btn)
    bot.send_message(chat_id=call.message.chat.id, text='Выберите конечную валюту:'
                     , reply_markup=keyboard)

@bot.callback_query_handler(func=lambda call: call.data[-6:] == 'finish')
def get_end_currency(call):
    selected_currency["to"] = call.data[:-7]
    msg = bot.send_message(chat_id=call.message.chat.id, text='Введите количество:')
    bot.register_next_step_handler(msg, get_amount)

def get_amount(message):
    selected_currency["amount"] = message.text

    print(selected_currency)

bot.polling()
