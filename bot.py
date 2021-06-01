import telebot
from telebot import types
import config
import requests
# import json
from datetime import datetime
from pprint import pprint

bot = telebot.TeleBot(config.token)

keyboard1 = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
popular_button = types.KeyboardButton("Що зараз популярне?\U0001F929")
love_button = types.KeyboardButton("Що любиш ти?\U0001F970")
cinema_button = types.KeyboardButton("Що зараз в кіношці?\U0001F3AC")
keyboard1.add(popular_button, cinema_button, love_button)

keyboard2 = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
more_button = types.KeyboardButton("Показати більше\U0001F9D0")
beginning_button = types.KeyboardButton("Показати спочатку\U0001F501")
menu_button = types.KeyboardButton("Головне меню\U0001F519")
keyboard2.add(more_button, beginning_button, menu_button)

user_dict = {}

def film_genre(genre_ids):
    genres = []
    for genre in config.genres:
        if genre['id'] in genre_ids:
            genres.append(genre['name'])
            if len(genres) == len(genre_ids):
                break
    return ', '.join(genres)


def sort_by(data, by):
    for d in data['results']:
        d[by] = float(d[by])
    data['results'] = sorted(data['results'], key=lambda k: k[by], reverse=True)


def send_popular(message, data):
    msg = bot.send_photo(message.chat.id, 'https://image.tmdb.org/t/p/w500' + data['poster_path'],
                         caption=f'Назва: {data["title"]}\n' \
                                 f'Жанр: {film_genre(data["genre_ids"])}\n' \
                                 f'Рік: {datetime.strptime(data["release_date"], "%Y-%m-%d").year}\n' \
                                 f'Оригінальна назва: {data["original_title"]}\n' \
                                 f'Рейтинг TMDB: {data["vote_average"]}',
                         reply_markup=keyboard2)
    return msg


def show(row_start, row_end, message, data):
    msg = None
    for i in range(row_start, row_end):
        msg = send_popular(message, data['results'][i])
    return msg


@bot.message_handler(commands=['start'])
def welcome(message):
    bot.send_message(message.chat.id, 'Привіт\U0001F590\nДай вгадаю, ти знову не знаєш, що подивитися?\U0001F631\n'
                                      'Не біда! Зі мною ти точно зробиш правильний вибір\U0001F609',
                     reply_markup=keyboard1)


@bot.message_handler(content_types=['text'])
def movie_rec(message):
    if message.text == "Що зараз популярне?\U0001F929":
        r = requests.get(f'https://api.themoviedb.org/3/movie/popular?api_key={config.api_key_tmdb}&'
                         f'language=ru&region=UA')
        data = r.json()
        sort_by(data, 'vote_average')

        bot.send_message(message.chat.id,
                         f'Тут тільки найпопулярніше\U0001F4A3\n')
        if user_dict.get(message.chat.id, 0) == 0:
            user_dict[message.chat.id] = {'row_start_popular': 0,
                                          'row_end_popular': 3,
                                          'love_films': {},
                                          'row_start_cinema': -3,
                                          'row_end_cinema': 0,
                                          'best_films': []}
        else:
            user_dict[message.chat.id]['row_start_popular'] += 3
            user_dict[message.chat.id]['row_end_popular'] += 3

        msg = show(user_dict[message.chat.id]['row_start_popular'], user_dict[message.chat.id]['row_end_popular'],
                   message, data)

        bot.register_next_step_handler(msg, process_popular, data)

    elif message.text == "Що любиш ти?\U0001F970":
        if user_dict.get(message.chat.id, 0) == 0:
            user_dict[message.chat.id] = {'row_start_popular': -3,
                                          'row_end_popular': 0,
                                          'love_films': {},
                                          'row_start_cinema': -3,
                                          'row_end_cinema': 0,
                                          'best_films': []}
        msg = bot.send_message(message.chat.id,
                               "Маєш найлубленіший фільм? Знайди схожий\U0001F4AF\n"
                               "Для цього просто введи його назву російською мовою\U0001F58B",
                               reply_markup=keyboard2)

        bot.register_next_step_handler(msg, process_love)

    elif message.text == "Що зараз в кіношці?\U0001F3AC":
        if user_dict.get(message.chat.id, 0) == 0:
            user_dict[message.chat.id] = {'row_start_popular': -3,
                                          'row_end_popular': 0,
                                          'love_films': {},
                                          'row_start_cinema': 0,
                                          'row_end_cinema': 3,
                                          'best_films': []}
        else:
            user_dict[message.chat.id]['row_start_cinema'] += 3
            user_dict[message.chat.id]['row_end_cinema'] += 3

        r = requests.get(f'https://api.themoviedb.org/3/movie/now_playing?api_key={config.api_key_tmdb}&'
                         f'region=UA&language=ru')
        data = r.json()
        sort_by(data, 'vote_average')
        pprint(data)

        bot.send_message(message.chat.id, f'Бііігом у кіно\U0001F3C3')
        msg = show(user_dict[message.chat.id]['row_start_cinema'], user_dict[message.chat.id]['row_end_cinema'],
                   message, data)
        bot.register_next_step_handler(msg, process_cinema, data)
    else:
        bot.send_message(message.chat.id, f'Фільм - це життя, із якого вивели плями нудьги\U0001F446',
                         reply_markup=keyboard1)


def process_popular(message, data):
    if message.text == "Показати більше\U0001F9D0":
        user_dict[message.chat.id]['row_start_popular'] += 3
        user_dict[message.chat.id]['row_end_popular'] += 3
        msg = show(user_dict[message.chat.id]['row_start_popular'], user_dict[message.chat.id]['row_end_popular'],
                   message, data)

        bot.register_next_step_handler(msg, process_popular, data)
        return

    elif message.text == "Показати спочатку\U0001F501":
        user_dict[message.chat.id]['row_start_popular'] = 0
        user_dict[message.chat.id]['row_end_popular'] = 3
        msg = show(user_dict[message.chat.id]['row_start_popular'], user_dict[message.chat.id]['row_end_popular'],
                   message, data)

        bot.register_next_step_handler(msg, process_popular, data)
        return

    else:
        bot.send_message(message.chat.id,
                         "А в кіно не хочеш сходити?\U0001F643",
                         reply_markup=keyboard1)


def process_love(message, data=None, the_most_similar=None):
    if message.text == "Головне меню\U0001F519":
        bot.send_message(message.chat.id,
                         'Чур, я буду дивитися фільм з тобою\U0001F916',
                         reply_markup=keyboard1)

    elif message.text == "Показати більше\U0001F9D0":
        if data is None:
            msg = bot.send_message(message.chat.id, 'А назву я буду вводити?\U0001F60F')
            bot.register_next_step_handler(msg, process_love)
            return

        msg = show(user_dict[message.chat.id]['love_films'][int(the_most_similar)]['row_start_love'],
                   user_dict[message.chat.id]['love_films'][int(the_most_similar)]['row_end_love'], message, data)
        user_dict[message.chat.id]['love_films'][int(the_most_similar)]['row_start_love'] += 3
        user_dict[message.chat.id]['love_films'][int(the_most_similar)]['row_end_love'] += 3

        bot.register_next_step_handler(msg, process_love, data, the_most_similar)
        return

    elif message.text == "Показати спочатку\U0001F501":
        if data is None:
            msg = bot.send_message(message.chat.id, 'А назву я буду вводити?\U0001F60F')
            bot.register_next_step_handler(msg, process_love)
            return

        user_dict[message.chat.id]['love_films'][int(the_most_similar)]['row_start_love'] = 0
        user_dict[message.chat.id]['love_films'][int(the_most_similar)]['row_end_love'] = 3

        msg = show(user_dict[message.chat.id]['love_films'][int(the_most_similar)]['row_start_love'],
                   user_dict[message.chat.id]['love_films'][int(the_most_similar)]['row_end_love'], message, data)

        bot.register_next_step_handler(msg, process_love, data, the_most_similar)
        return

    else:
        r = requests.get(
            f'https://api.themoviedb.org/3/search/movie?api_key={config.api_key_tmdb}&language=ru&region=UA&'
            f'query={message.text}')
        data = r.json()

        if len(data['results']) == 0:
            msg = bot.send_message(message.chat.id, "Зібрав дані з усього інтернету, але так і не знайшов такого фільма"
                                                    "\U0001F97A\nМожливо, перевіриш правильність написання?\U0001F50D")
            bot.register_next_step_handler(msg, process_love)
            return

        sort_by(data, 'popularity')
        the_most_similar = data['results'][0]['id']
        # print(data['results'][0]['title'], data['results'][0]['overview'])
        if user_dict[message.chat.id]['love_films'].get(int(the_most_similar), -1) == -1:
            user_dict[message.chat.id]['love_films'][int(the_most_similar)] = {'row_start_love': 0,
                                                                               'row_end_love': 3}

        r1 = requests.get(
            f'https://api.themoviedb.org/3/movie/{int(the_most_similar)}/recommendations?api_key={config.api_key_tmdb}&'
            f'language=ru&region=UA')
        data = r1.json()
        if len(data['results']) == 0:
            msg = bot.send_message(message.chat.id, 'Це неповторний фільм, схожих ти більше не побачиш\U0001F937')
            bot.register_next_step_handler(msg, process_love)
            return

        bot.send_message(message.chat.id, "Уххх, які фільми я знайшов\U0001F525\U0001F525\U0001F525")
        msg = show(user_dict[message.chat.id]['love_films'][int(the_most_similar)]['row_start_love'],
                   user_dict[message.chat.id]['love_films'][int(the_most_similar)]['row_end_love'], message, data)
        user_dict[message.chat.id]['love_films'][int(the_most_similar)]['row_start_love'] += 3
        user_dict[message.chat.id]['love_films'][int(the_most_similar)]['row_end_love'] += 3

        bot.register_next_step_handler(msg, process_love, data, the_most_similar)
        return


def process_cinema(message, data):
    if message.text == "Показати більше\U0001F9D0":
        user_dict[message.chat.id]['row_start_cinema'] += 3
        user_dict[message.chat.id]['row_end_cinema'] += 3
        msg = show(user_dict[message.chat.id]['row_start_cinema'], user_dict[message.chat.id]['row_end_cinema'],
                   message, data)

        bot.register_next_step_handler(msg, process_cinema, data)
        return
    elif message.text == "Показати спочатку\U0001F501":
        user_dict[message.chat.id]['row_start_cinema'] = 0
        user_dict[message.chat.id]['row_end_cinema'] = 3
        msg = show(user_dict[message.chat.id]['row_start_cinema'], user_dict[message.chat.id]['row_end_cinema'],
                   message, data)

        bot.register_next_step_handler(msg, process_cinema, data)
        return

    else:
        bot.send_message(message.chat.id,
                         'Ну зізнавайся, уже купив квитки в кіно?\U0001F3AB',
                         reply_markup=keyboard1)


if __name__ == '__main__':
    bot.infinity_polling()
