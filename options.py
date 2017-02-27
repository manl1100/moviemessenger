from tornado.options import options, define

define('app_secret', default='', type=str)
define('page_access_token', default='', type=str)
define('validation_token', default='', type=str)
define('server_url', default='', type=str)

options.parse_config_file("server.conf")
