from tornado import gen
from tornado.httpclient import HTTPRequest, AsyncHTTPClient
from datetime import date, timedelta
from tornado.httpclient import HTTPRequest, AsyncHTTPClient
from tornado.escape import json_decode
from options import options
import urllib


@gen.coroutine
def fetch_movies_from_api():

    httpclient = AsyncHTTPClient()
    url = 'https://api.themoviedb.org/3/discover/movie?'
    start_date = date.today()
    end_date = date.today() + timedelta(days=7)
    params = {
        'primary_release_date.gte': start_date.strftime('%Y-%m-%d'),
        'primary_release_date.lte': end_date.strftime('%Y-%m-%d'),
        'api_key': options.movie_db_api,
        'region': 'US',
        'sort_by': 'popularyity.desc'
    }
    request = HTTPRequest(url + urllib.urlencode(params))
    response = yield httpclient.fetch(request)

    data = json_decode(response.body)
    titles = []
    for result in data['results']:
        if result['poster_path'] is None:
            continue

        movie = {
            'title': result['title'],
            'release_date': result['release_date'],
            'poster_url': 'http://image.tmdb.org/t/p/w500' + result['poster_path'],
        }
        titles.append(movie)

    raise gen.Return(titles)


class Movie(object):

    def __init__(self, title, image_url):
        self.title = title
        self.image_url = image_url
