import json
import urllib
from datetime import date
from tornado.web import RequestHandler
from tornado.escape import json_decode
from tornado.httpclient import HTTPRequest, AsyncHTTPClient
from options import options


class MovieHandler(RequestHandler):

    def get(self):
        if self.get_argument('hub.mode') == 'subscribe' and self.get_argument('hub.verify_token') == options.validation_token:
            self.write(self.get_argument('hub.challenge'))
        else:
            self.set_status(403)
            self.finish()

    def post(self):
        data = json_decode(self.request.body)

        if data['object'] != 'page':
            return

        for entry in data['entry']:
            page_id = entry['id']
            time_of_event = entry['time']

            for message in entry['messaging']:
                if 'message' in message:
                    self.process_message(message)
                elif 'postback' in message:
                    self.process_postback(message)
                else:
                    print message

        self.finish()

    def process_message(self, event):
        sender_id = event['sender']['id']
        message_text = event['message']['text']

        if message_text is not None:
            if message_text == 'movies this week':
                self.fetch_current_movies(sender_id)
            elif message_text == 'movies out now':
                self.send_text_message(sender_id, message_text)
            else:
                self.send_text_message(sender_id, message_text)

    def fetch_current_movies(self, sender_id):
        httpclient = AsyncHTTPClient()
        url = 'https://api.themoviedb.org/3/discover/movie?'
        params = {
            'primary_release_date.gte': date.today().strftime('%Y-%m-%d'),
            'primary_release_date.lte': date.today().strftime('%Y-%m-%d'),
            'api_key': options.movie_db_api,
        }
        request = HTTPRequest(url + urllib.urlencode(params))

        def send_current_movies(response):
            data = json_decode(response.body)
            titles = []
            for result in data['results']:
                titles.append(result['title'])
            self.send_text_message(sender_id, ','.join(titles))

        response = httpclient.fetch(request, callback=send_current_movies)

    def send_text_message(self, recipient_id, message_text):
        message = {
            'recipient': {
                'id': recipient_id,
            },
            'message': {
                'attachment': {
                    'type': 'template',
                    'payload': {
                        'template_type': 'generic',
                        'elements': [{
                            'title': 'title',
                            'subtitle': 'Subtitle',
                            'item_url': 'https://www.google.com',
                            'image_url': 'https://www.google.com',
                            'buttons': [{
                                'type': 'web_url',
                                'url': 'https://www.google.com',
                                'title': 'title',
                            }, {
                                'type': 'postback',
                                'title': 'Call postback',
                                'payload': 'payload',
                            }]
                        }, {
                            'title': 'title',
                            'subtitle': 'Subtitle',
                            'item_url': 'https://www.google.com',
                            'image_url': 'https://www.google.com',
                            'buttons': [{
                                'type': 'web_url',
                                'url': 'https://www.google.com',
                                'title': 'title',
                            }, {
                                'type': 'postback',
                                'title': 'Call postback',
                                'payload': 'payload',
                            }]
                        }]
                    }
                }
            }
        }

        self.send_request(message)

    def send_request(self, payload):
        httpclient = AsyncHTTPClient()
        headers = {'Content-type': 'application/json'}
        request = HTTPRequest('https://graph.facebook.com/v2.6/me/messages?access_token=%s' % (options.page_access_token),
                              method='POST', headers=headers, body=json.dumps(payload))

        # will switch to futures in the future..
        response = httpclient.fetch(request, callback=self.handle_response)

    def handle_response(self, response):
        if response.error:
            print response
        else:
            print response.body

    def process_postback(self, postback):
        pass
