


import io, os, json
import secrets, random

import tornado.web
import tornado.httpserver
import tornado.httpclient

from motor.motor_tornado import MotorClient

from dotenv import load_dotenv
load_dotenv()

class BaseHandler(tornado.web.RequestHandler):
    client = MotorClient(os.getenv('MONGO_URI'))
    database = client['clipboard-app']
    clipboards = database['clipboards']

    def set_default_headers(self):
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "*")
        self.set_header('Access-Control-Allow-Methods', 'POST, GET, DELETE, OPTIONS')
    
    def options(self, *args):
        self.set_status(204)
        self.finish()
    
class Index(BaseHandler):
    async def get(self):
        resp = {
            "success": True,
            "message": "Clipboard API Root. https://clipboard-app.netlify.app",
            "data": {}
        }
        self.write(resp)

class Clipboard(BaseHandler):
    async def get(self, clipboard_id):

        try:
            cursor = self.clipboards.find({'clipboard_id': clipboard_id})
            result = await cursor.to_list(None)
            if result:
                selected = result[0]
                clipboard = {
                    'clipboard_id': selected['clipboard_id'],
                    'items': selected['items']
                }

                resp = {
                    'success': True,
                    'message': f'Opened clipboard {clipboard_id}',
                    'data': clipboard
                }
                return self.write(resp)
            else:
                result = await self.clipboards.insert_one(
                    {'clipboard_id': clipboard_id, 'items': []}
                )
                clipboard = {'clipboard_id': clipboard_id, 'items': []}

                resp = {
                    'success': True,
                    'message': f'Opened clipboard {clipboard_id}',
                    'data': clipboard
                }
                return self.write(resp)
            
        except:
            # raise
            resp = {
                'success': False,
                'message': 'Failed to open clipboard',
                'errors': [
                    {'message': 'Server error'}
                ]
            }
            self.write(resp)
    
    async def delete(self, clipboard_id):
        
        try: 
            result = await self.clipboards.delete_one({'clipboard_id': clipboard_id})
            if result.deleted_count:
                resp = {
                    'success': True,
                    'message': f'Deleted clipboard {clipboard_id}',
                }
                return self.write(resp)
            else:
                resp = {
                    'success': False,
                    'message': 'Failed to delete clipboard',
                    'errors': [
                        {
                            'message': f'Clipboard does not exist'
                        }
                    ]
                }
                return self.write(resp)
        except:
            resp = {
                'success': False,
                'message': 'Failed to delete clipboard',
                'errors': [
                    {
                        'message': 'Server error'
                    }
                ]
            }
            return self.write(resp)

class Item(BaseHandler):
    async def post(self, clipboard_id):
        
        try:
            data = json.loads(self.request.body)
            item = {
                'id': data['id'],
                'content': data['content']
            }

            result = await self.clipboards.update_one(
                {'clipboard_id': clipboard_id},
                {'$push': {'items': item}}
            )
            if not result.modified_count:
                resp = {
                    'success': False,
                    'message': 'Failed to add item to clipboard',
                    'errors': [
                        {
                            'message': 'Clipboard identifier is invalid'
                        }
                    ]
                }
                return self.write(resp)
            else:
                resp = {
                    'success': True,
                    'message': 'Item added to clipboard',
                }
                return self.write(resp)

        except json.JSONDecodeError:
            resp = {
                'success': False,
                'message': 'Failed to add item to clipboard',
                'errors': [
                    {
                        'message': 'Failed to parse request data'
                    }
                ]
            }
            return self.write(resp)

        except:
            resp = {
                'success': False,
                'message': 'Failed to add item to clipboard',
                'errors': [
                    {
                        'message': 'Server error'
                    }
                ]
            }
            return self.write(resp)

    async def delete(self, clipboard_id):
        data = json.loads(self.request.body)
        item_id = data.get('id', None)
        if not item_id:
            resp = {
                'success': False,
                'message': 'Item ID not specified',
                'errors': [
                    {
                        'message': 'ID of item to be deleted must be provided'
                    }
                ]
            }
            return self.write(resp)
        
        try:
            result = await self.clipboards.update_one(
                {'clipboard_id': clipboard_id},
                {'$pull': {'items': {'id': item_id}}}
            )
            if not result.modified_count:
                # the problem here could have been from an invalid clipboard_id or item_id
                resp = {
                    'success': False,
                    'message': 'Failed to remove item from clipboard',
                    'errors': [
                        {
                            'message': 'Clipboard ID or ID of item is invalid'
                        }
                    ]
                }
                return self.write(resp)
            else:
                resp = {
                    'success': True,
                    'message': 'Removed item from clipboard',
                }
                return self.write(resp)

        except:
            resp = {
                'success': False,
                'message': 'Failed to remove item from clipboard',
                'errors': [
                    {
                        'message': 'Server error'
                    }
                ]
            }
            return self.write(resp)

from tornado.options import define
define("port", default="8080", type=str)

handlers = [
    (r"/", Index),
    (r"/clipboard/([0-9a-z]+)", Clipboard),
    (r"/clipboard/([0-9a-z]+)/items", Item)
]


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