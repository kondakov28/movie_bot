from config import api_key_tmdb
import requests
from pprint import pprint


def today():
    r = requests.get(f'https://api.themoviedb.org/3/movie/now_playing?api_key={api_key_tmdb}&region=UA&language=ru')
    data = r.json()
    for d in data['results']:
        d['vote_average'] = float(d['vote_average'])
    data['results'] = sorted(data['results'], key=lambda k: k['vote_average'], reverse=True)
    # titles = {}
    # for result in data['results']:
    #     titles[result['title']] = result['popularity']
    # sort_titles = sorted(titles.items(), key=lambda x: x[1], reverse=True)
    # print(dict(sort_titles))
    pprint(data)


def genres():
    r = requests.get(f'https://api.themoviedb.org/3/genre/movie/list?api_key={api_key_tmdb}&language=ru')
    data = r.json()
    pprint(data)


def get_recommendation(film_id):
    r = requests.get(f'https://api.themoviedb.org/3/movie/{film_id}/recommendations?api_key={api_key_tmdb}&language=ru')
    data = r.json()
    pprint(data)


def top_rated():
    r = requests.get(f'https://api.themoviedb.org/3/movie/top_rated?api_key={api_key_tmdb}&language=ru')
    data = r.json()
    pprint(data)


def popular():
    r = requests.get(f'https://api.themoviedb.org/3/movie/popular?api_key={api_key_tmdb}&language=ru&region=UA')
    data = r.json()
    pprint(data)


def upcoming():
    r = requests.get(f'https://api.themoviedb.org/3/movie/upcoming?api_key={api_key_tmdb}&language=ru&region=UA')
    data = r.json()
    pprint(data)


def search(movie):
    r = requests.get(f'https://api.themoviedb.org/3/search/movie?api_key={api_key_tmdb}&language=ru&region=UA&query={movie}')
    data = r.json()
    pprint(data)


def people():
    r = requests.get(
        f'https://api.themoviedb.org/3/search/person?api_key={api_key_tmdb}&language=ru&region=UA&query={"джеймс кэмерон"}')
    data = r.json()
    pprint(data)


if __name__ == '__main__':
    people()