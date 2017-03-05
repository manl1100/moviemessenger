import json
from tornado.web import RequestHandler
from tornado.escape import json_decode
from tornado.httpclient import HTTPRequest, AsyncHTTPClient
from options import options
from tornado import gen
from movies import fetch_movies_from_api


class FacebookHandler(RequestHandler):

    def get(self):
        if self.get_argument('hub.mode') == 'subscribe' and self.get_argument('hub.verify_token') == options.validation_token:
            self.write(self.get_argument('hub.challenge'))
        else:
            self.set_status(403)
            self.finish()

    @gen.coroutine
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

    @gen.coroutine
    def process_message(self, event):
        sender_id = event['sender']['id']
        message_text = event['message']['text']

        if message_text is not None:
            if message_text == 'movies this week':
                self.respond_with_current_movies(sender_id)
            elif message_text == 'movies out now':
                self.send_text_message(sender_id, message_text)
            else:
                self.send_text_message(sender_id, message_text)

    @gen.coroutine
    def respond_with_current_movies(self, sender_id):
        movies = yield fetch_movies_from_api()
        self.send_generic_messsage(sender_id, movies)

    def send_generic_messsage(self, recipient_id, movies):
        elements = []
        for movie in movies:
            element = {
                'title': movie.title,
                'subtitle': movie.release_date,
                'item_url': 'https://www.google.com',
                'image_url': movie.poster_url,
                'buttons': [{
                    'type': 'web_url',
                    'url': 'https://www.google.com',
                    'title': 'Take me to google'
                }]
            }
            elements.append(element)

        message = {
            'recipient': {
                'id': recipient_id,
            },
            'message': {
                'attachment': {
                    'type': 'template',
                    'payload': {
                        'template_type': 'generic',
                        'image_aspect_ratio': 'square',
                        'elements': elements
                    }
                }
            }
        }
        self.send_request(message)

    def send_text_message(self, recipient_id, message_text):
        message = {
            'recipient': {
                'id': recipient_id,
            },
            'message': {
                'text': message_text,
                'metadata': 'DEVELOPER_DEFINED_METADATA',
            }
        }

        self.send_request(message)

    @gen.coroutine
    def send_request(self, payload):
        httpclient = AsyncHTTPClient()
        headers = {'Content-type': 'application/json'}
        request = HTTPRequest('https://graph.facebook.com/v2.6/me/messages?access_token=%s' % (options.page_access_token),
                              method='POST', headers=headers, body=json.dumps(payload))

        response = yield httpclient.fetch(request)

    def process_postback(self, postback):
        pass
