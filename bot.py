import telebot
from config import TOKEN, currency_dict
from extensions import Converter, UserEnter
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup

bot = telebot.TeleBot(TOKEN)
selected_currency = {}


@bot.message_handler(commands=['start', ])
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


@bot.message_handler(commands=['help'])
def help_command(message: telebot.types.Message):
    bot_help(message)


@bot.callback_query_handler(func=lambda call: call.data == 'help')
def help_callback(call):
    bot_help(call.message)


def bot_help(message):
    text = '''Конвертер валют - это бот, который позволяет получить актуальный 
курс валюты и произвести конвертацию. 

Шаг 1: Для начала работы с ботом, нажмите кнопку "начать".

Шаг 2: Выберите начальную валюту, которую хотите конвертировать.

Шаг 3: Выберите конечную валюту, в которую хотите произвести конвертацию.

Шаг 4: Введите сумму начальной валюты с помощью клавиатуры.

Шаг 5: Проверьте, все ли верно, и нажмите кнопку "конвертировать", 
чтобы получить результат. 

Шаг 6: Если хотите поменять значения, нажмите кнопку "заново".

Шаг 7: Посмотрите результат конвертации. Если хотите повторить,
нажмите кнопку "ещё раз". '''

    keyboard = InlineKeyboardMarkup()
    btn1 = InlineKeyboardButton('начать', callback_data='begin')
    keyboard.add(btn1)

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
        # уникальный callback для начальной валюты
        btn = telebot.types.InlineKeyboardButton(i, callback_data=f'{i} start')
        keyboard.add(btn)

    bot.send_message(chat_id=message.chat.id, text='Выберите начальную валюту:'
                     , reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: call.data[-5:] == 'start')
def get_start_currency(call):
    selected_currency["from"] = call.data[:-6]
    keyboard = InlineKeyboardMarkup()
    for i in currency_dict.keys():
        # убираем начальную валюту
        if i != selected_currency['from']:
            # уникальный callback для конечной валюты
            btn = telebot.types.InlineKeyboardButton(i,
                                                     callback_data=f'{i} '
                                                                   f'finish')
            keyboard.add(btn)
    bot.send_message(chat_id=call.message.chat.id,
                     text='Выберите конечную валюту:'
                     , reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: call.data[-6:] == 'finish')
def get_end_currency(call):
    selected_currency["to"] = call.data[:-7]
    msg = bot.send_message(chat_id=call.message.chat.id,
                           text='Введите количество:')
    bot.register_next_step_handler(msg, get_amount)


def get_amount(message):
    selected_currency["amount"] = message.text
    text = f'начальная валюта: {selected_currency.get("from")} ' \
           f'\nконечная валюта: {selected_currency.get("to")} ' \
           f'\nколичество начальной валюты: {selected_currency.get("amount")}'

    keyboard = InlineKeyboardMarkup()
    btn = telebot.types.InlineKeyboardButton("конвертировать",
                                             callback_data='convert')
    keyboard.add(btn)
    btn = telebot.types.InlineKeyboardButton("заново",
                                             callback_data='begin')
    keyboard.add(btn)
    bot.send_message(chat_id=message.chat.id, text=text, reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: call.data == 'convert')
def convert(call):
    try:
        if not selected_currency.get("amount").isdigit():
            raise UserEnter()

        data = Converter.get_price(selected_currency.get("to"),
                                   selected_currency.get("from"),
                                   int(selected_currency.get("amount")))

        rate = data.get('info').get('rate')
        total = data.get('result')
        text = f'{selected_currency.get("amount")} ' \
               f'{selected_currency.get("from")}' \
               f' = {total} {selected_currency.get("to")} \nпо курсу {rate}'
        keyboard = InlineKeyboardMarkup()
        btn = telebot.types.InlineKeyboardButton("ещё раз",
                                                 callback_data='begin')
        keyboard.add(btn)
        bot.send_message(chat_id=call.message.chat.id, text=text,
                         reply_markup=keyboard)
    except UserEnter:
        text = 'Ошибка формирования запроса, количество валюты вводится ' \
               'только цифрами!!! '
        bot.send_message(chat_id=call.message.chat.id, text=f'{text}')


bot.polling()
