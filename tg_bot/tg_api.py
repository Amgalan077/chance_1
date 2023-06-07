import config
import telebot
from telebot import types
from site_api import site_api_handler

bot = telebot.TeleBot(config.BOT_TOKEN)
hotels_btn = {}
args = None
sort_ = None
price_range = None  # для диапозона цен
distance_range = None  # для диапозона расстояний
amount_hotels = None  # для количество отелей
bestdeal_city = None
commads = None  # для low,high = 0; для best = 1

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
    markup = types.ReplyKeyboardMarkup(row_width=2)
    btn1 = types.KeyboardButton('/lowprice')
    btn2 = types.KeyboardButton('/highprice')
    btn3 = types.KeyboardButton('/bestdeal')
    btn4 = types.KeyboardButton('/history')
    markup.row(btn1, btn2)
    markup.row(btn3, btn4)
    bot.send_message(message.chat.id,
                     'Добро пожаловать в бота по поиску отелей.\nВыберите команду:', reply_markup=markup)
    # bot.register_next_step_handler(message, get_hotels)


@bot.message_handler(func=lambda message: message.text == 'Вернуться обратно в меню')
def start_1(message):
    markup = types.ReplyKeyboardMarkup(row_width=2)
    btn1 = types.KeyboardButton('/lowprice')
    btn2 = types.KeyboardButton('/highprice')
    btn3 = types.KeyboardButton('/bestdeal')
    btn4 = types.KeyboardButton('/history')
    markup.row(btn1, btn2)
    markup.row(btn3, btn4)
    bot.send_message(message.chat.id,
                     'Выберите другую команду:', reply_markup=markup)


@bot.message_handler(commands=['lowprice'])
def get_hotels_lowprice(message):
    global args, sort_, commads
    commads = 0
    bot.send_message(message.chat.id, 'Введите город и через пробел количество отелей.\nПример: "Рига 2"')
    bot.register_next_step_handler(message, answer_from_user)
    bot.register_next_step_handler(message, lambda message: process_callback_data(message, 'low'))


@bot.message_handler(commands=['highprice'])
def get_hotels_highprice(message):
    global args, sort_, commads
    commads = 0
    bot.send_message(message.chat.id, 'Введите город и через пробел количество отелей.\nПример: "Рига 2"')
    bot.register_next_step_handler(message, answer_from_user)
    bot.register_next_step_handler(message, lambda message: process_callback_data(message, 'high'))


@bot.message_handler(commands=['bestdeal'])
def get_hotels(message):
    global commads
    commads = 1
    bot.send_message(message.chat.id, 'Введите город:')
    bot.register_next_step_handler(message, answer_price_range)


def answer_from_user(message):  # для /lowprice и /highprice
    global args
    args = message.text.split()  # Текст пользователя: Рига 2


def answer_price_range(message):  # для /bestdeal
    global bestdeal_city
    bestdeal_city = message.text
    bot.send_message(message.chat.id, 'Введите диапозон цен, где первая цифра начало, вторая - конец\nПример: 1 40')
    bot.register_next_step_handler(message, get_price_range)


def get_price_range(message):  # диапозон цен (bestdeal)
    global price_range
    price_range = message.text.split()
    # print(price_range)
    bot.send_message(message.chat.id,
                     'Введите диапозон расстояния (в метрах), где первая цифра начало, вторая - конец\nПример: 20 100')
    bot.register_next_step_handler(message, get_distance_range)


def get_distance_range(message):  # диапозон расстояний (bestdeal)
    global distance_range
    distance_range = message.text.split()
    # print(distance_range)
    bot.send_message(message.chat.id, 'Введите кол-во отелей')
    bot.register_next_step_handler(message, get_amount_hotels)


def get_amount_hotels(message):  # количество отелей
    global amount_hotels, price_range, args, bestdeal_city
    amount_hotels = message.text
    args = [bestdeal_city, amount_hotels]
    # print(args)
    process_callback_data(message, price_range[0], price_range[1], 'low')


def process_callback_data(message, min_price: int = 100, max_price: int = 150, sortirovka='low'):
    global args, sort_, commads
    sort_ = sortirovka
    try:
        city, num_hotels = args[0], int(args[1])  # Разделение текста на аргументы
        print(min_price, max_price)
        hotels_data = site_api_handler.get_hotels_in_city(city, num_hotels, int(min_price), int(max_price), sort_, commads)
        hotels_data_text = '\n'.join([hotel for hotel in hotels_data])

        keyboard = create_hotel_buttons(hotels_data)  # создание кнопок с помощью функции
        if len([hotel for hotel in hotels_data]) < num_hotels:  # для проверки количество отелей
            bot.send_message(message.chat.id, f'{hotels_data_text}\nВсе, что есть', reply_markup=keyboard)
        else:
            bot.send_message(message.chat.id, f'{hotels_data_text}', reply_markup=keyboard)

    except ValueError:
        bot.send_message(message.chat.id, 'Введите все заново! (Город число)')
        bot.register_next_step_handler(message, start)


@bot.callback_query_handler(func=lambda call: call.data.isdigit())
def callback(call):
    bot.send_message(call.message.chat.id, 'Введите, сколько фототографии вам нужно:')
    bot.register_next_step_handler(call.message, lambda message: get_num_photo(message, call.data))


def get_num_photo(message, data):
    num_photo = int(message.text)
    res = site_api_handler.print_hotels(data, num_photo)
    markup = types.ReplyKeyboardMarkup()
    btn1 = types.KeyboardButton('Вернуться обратно в меню')
    markup.row(btn1)
    for info, url in res.items():
        bot.send_photo(message.chat.id, url, caption=info, reply_markup=markup)


bot.infinity_polling()
