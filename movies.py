from tornado import gen
from tornado.httpclient import HTTPRequest, AsyncHTTPClient
from datetime import date, timedelta
from tornado.httpclient import HTTPRequest, AsyncHTTPClient
from tornado.escape import json_decode
from options import options
import urllib

URL = 'https://api.themoviedb.org/3/discover/movie?'

POSTER_BASE_URL = 'http://image.tmdb.org/t/p/w500'


@gen.coroutine
def fetch_movies_from_api():
    httpclient = AsyncHTTPClient()

    start_date = date.today()
    end_date = date.today() + timedelta(days=7)
    params = {
        'primary_release_date.gte': start_date.strftime('%Y-%m-%d'),
        'primary_release_date.lte': end_date.strftime('%Y-%m-%d'),
        'api_key': options.movie_db_api,
        'region': 'US',
        'sort_by': 'popularyity.desc'
    }

    request = HTTPRequest(URL + urllib.urlencode(params))
    response = yield httpclient.fetch(request)

    data = json_decode(response.body)
    titles = []
    for result in data['results']:
        if result['poster_path'] is None:
            continue

        poster_url = POSTER_BASE_URL + result['poster_path']
        titles.append(
            Movie(result['title'], poster_url, result['release_date']))

    raise gen.Return(titles)


class Movie(object):

    def __init__(self, title, poster_url, release_date):
        self.title = title
        self.poster_url = poster_url
        self.release_date = release_date
