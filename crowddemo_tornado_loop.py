import ujson

import zmq
from zmq.eventloop import ioloop, zmqstream
"""
ioloop.install() must be called prior to instantiating *any* tornado objects,
and ideally before importing anything from tornado, just to be safe.
install() sets the singleton instance of tornado.ioloop.IOLoop with zmq's
IOLoop. If this is not done properly, multiple IOLoop instances may be
created, which will have the effect of some subset of handlers never being
called, because only one loop will be running.
"""
ioloop.install()

import tornado
from tornado import websocket, web

from app_settings import settings, zmq_router_fe, ws_tcp_port
cl = []

def printer(msg):
    print "ZMQ Received: %s" % msg

ctx = zmq.Context()
s = ctx.socket(zmq.REQ)
s.connect('tcp://127.0.0.1:%d' % zmq_router_fe)
stream = zmqstream.ZMQStream(s)
stream.on_recv(printer)

class IndexHandler(web.RequestHandler):
    def get(self):
        self.render("app\\multi_brad_scene.html")

class SocketHandler(websocket.WebSocketHandler):
    def check_origin(self, origin):
        return True

    def open(self):
        if self not in cl:
            cl.append(self)
        print("...WebSocket opened!")
        stream.on_recv(self.send_update)

    def on_close(self):
        if self not in cl:
            cl.remove(self)
        print("WebSocket closed")
        stream.on_recv(self.send_update)

    def on_message(self, message):
        print("Received: " + message)
        m = ujson.loads(message)
        cmd = m['command']
        print("...Command: " + cmd)
        if cmd=='update':
            dtime = str(m['data'])
            stream.send_multipart([b"update", dtime])


    def send_update(self, msg):
        resp = msg[0]
        print "ZMQ Received: %s" % resp
        self.write_message(resp)


app = web.Application([
    (r'/', IndexHandler),
    (r'/ws', SocketHandler),
    (r'/js/(.*)',web.StaticFileHandler, {'path': './app/js'},),
    (r'/models/(.*)',web.StaticFileHandler, {'path': './app/models'},)
], **settings)

if __name__ == '__main__':
    app.listen(ws_tcp_port)
    print "Listening on %d..." % ws_tcp_port

    try:
        ioloop.IOLoop.instance().start()
    except KeyboardInterrupt:
        print ' Interrupted'
