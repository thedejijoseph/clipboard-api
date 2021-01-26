


import io, os, json
import secrets, random

import tornado.web
import tornado.httpserver
import tornado.httpclient

from motor.motor_tornado import MotorClient

from dotenv import load_dotenv

class BaseHandler(tornado.web.RequestHandler):
    client = ""
    
class Index(BaseHandler):
    def get(self):
        resp = {
            "success": True,
            "message": "Clipboard API Root. https://clipboard-app.netlify.app",
            "data": {}
        }
        self.write(resp)

class Clipboard(BaseHandler):
    def get(self, clipboard_id):

        try:
            EMPTY_CLIPBOARD = {'clipboard_id': clipboard_id, 'items': []}

            clipboard = "get_clipboard"
            if not clipboard:
                clipboard = EMPTY_CLIPBOARD
            
            resp = {
                'success': True,
                'message': f'Opened clipboard {clipboard_id}',
                'data': clipboard
            }
            return self.write(resp)
        except:
            resp = {
                'success': False,
                'message': 'Failed to open clipboard',
                'errors': [
                    {'message': 'Server error'}
                ]
            }
    
    def delete(self, clipboard_id):
        
        try: 
            delete_clipboard = True
            if delete_clipboard:
                resp = {
                    'succss': True,
                    'message': f'Deleted clipboard {clipboard_id}',
                }
                return self.write(resp)
            else:
                resp = {
                    'success': False,
                    'message': 'Failed to delete clipboard'
                }
                return self.write(resp)
        except:
            resp = {
                'success': False,
                'message': 'Failed to delete clipboard'
            }
            return self.write(resp)

class Item(BaseHandler):
    def post(self, clipboard_id, item_id):
        pass

    def delete(self, clipboard_id, item_id):
        pass

from tornado.options import define
define("port", default=3300, type=int)

handlers = [
    (r"/", Index),
    (r"/clipboard/([0-9a-z]+)", Clipboard),
    (r"/clipboard/([0-9a-z]+)/items/([0-9a-z]+)", Item)
]

load_dotenv()

# switch debug mode on or off
try:
    var = os.environ['APP_STAGE']
    prod = True if var == 'PROD' else False
except:
    prod = False


settings = dict(
    debug = False if prod else True,
    cookie_secret = secrets.token_hex(16),
    template_path = os.path.join(os.path.dirname(__file__), "templates"),
    static_path = os.path.join(os.path.dirname(__file__), "static"),
    autoescape = None,
)

app = tornado.web.Application(handlers, **settings)
def start():
    try:
        tornado.options.parse_command_line()
        port = tornado.options.options.port
        server = tornado.httpserver.HTTPServer(app)
        server.listen(port)
        
        start_msg = f"Tornado server started. Port {port}"
        print('\n' + '=' * len(start_msg) + '\n' \
            + start_msg + '\n' + '=' * len(start_msg))
        
        tornado.ioloop.IOLoop.instance().start()
    except KeyboardInterrupt:
        stop_msg = "Stopping server..."
        print('\n' + '=' * len(stop_msg) + '\n' \
            + stop_msg + '\n' + '=' * len(stop_msg))
        import sys
        sys.exit()

if __name__ == "__main__":
    start()