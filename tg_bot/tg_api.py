import config
import telebot
from telebot import types
from site_api import site_api_handler

bot = telebot.TeleBot(config.BOT_TOKEN)
hotels_btn = {}
args = None
sort_ = None
"""
/lowprice: Сортировка по убыванию
/highprice: Сортировка по возрастанию


"""


def create_hotel_buttons(list_hotels):  # кнопки для отелей
    amount = 0
    markup = types.InlineKeyboardMarkup(row_width=2)

    for hotel in list_hotels:
        amount += 1
        btn = types.InlineKeyboardButton(f'{hotel}', callback_data=f'{list_hotels[hotel]}')
        markup.add(btn)
    return markup


@bot.message_handler(commands=['start'])
def start(message):
    markup = types.InlineKeyboardMarkup(row_width=2)
    btn1 = types.InlineKeyboardButton('/lowpice', callback_data='high')
    btn2 = types.InlineKeyboardButton('/highprice', callback_data='low')
    btn3 = types.InlineKeyboardButton('/bestdeal', callback_data='low')
    btn4 = types.InlineKeyboardButton('/history', callback_data='low')
    markup.row(btn1, btn2,btn3,btn4)
    bot.send_message(message.chat.id,
                     'Добро пожаловать в бота по поиску отелей.\nВыберите команду:')
    bot.register_next_step_handler(message, get_hotels)


@bot.message_handler(func=lambda message: message.text == 'Вернуться обратно к поиску отелей')
def start_1(message):
    bot.send_message(message.chat.id, 'Введите город и через пробел количество отелей.\nПример: "Рига 2"')
    bot.register_next_step_handler(message, get_hotels)


def get_hotels(message):
    global args,sort_
    args = message.text.split()  # Текст пользователя: Рига 2

    markup = types.InlineKeyboardMarkup(row_width=1)
    btn1 = types.InlineKeyboardButton('Сортировка по убыванию', callback_data='high')
    btn2 = types.InlineKeyboardButton('Сортировка по возрастанию', callback_data='low')
    markup.row(btn1, btn2)
    bot.send_message(message.chat.id, 'Сортировка:', reply_markup=markup)

    bot.register_next_step_handler(message, process_callback_data)




@bot.callback_query_handler(func=lambda call: call.data.isalpha())
def process_callback_data(call):
    global args, sort_
    sort_ = call.data
    try:
        city, num_hotels = args[0], int(args[1])  # Разделение текста на аргументы
        hotels_data = site_api_handler.get_hotels_in_city(city, num_hotels, sort_)
        hotels_data_text = '\n'.join([hotel for hotel in hotels_data])

        keyboard = create_hotel_buttons(hotels_data)  # создание кнопок с помощью функции
        if len([hotel for hotel in hotels_data]) < num_hotels:  # для проверки количество отелей
            bot.send_message(call.message.chat.id, f'{hotels_data_text}\nВсе, что есть', reply_markup=keyboard)
        else:
            bot.send_message(call.message.chat.id, f'{hotels_data_text}', reply_markup=keyboard)

    except ValueError:
        bot.send_message(callback.message.chat.id, 'Введите все заново! (Город число)')
        bot.register_next_step_handler(call.message, start)


@bot.callback_query_handler(func=lambda call: call.data.isdigit())
def callback(call):
    bot.send_message(call.message.chat.id, 'Введите, сколько фототографии вам нужно:')
    bot.register_next_step_handler(call.message, lambda message: get_num_photo(message, call.data))


def get_num_photo(message, data):
    num_photo = int(message.text)
    res = site_api_handler.print_hotels(data, num_photo)
    markup = types.ReplyKeyboardMarkup()
    btn1 = types.KeyboardButton('Вернуться обратно к поиску отелей')
    markup.row(btn1)
    for info, url in res.items():
        bot.send_photo(message.chat.id, url, caption=info, reply_markup=markup)

    # bot.register_next_step_handler(message, start)


bot.infinity_polling()
