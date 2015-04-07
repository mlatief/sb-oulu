#from gevent import monkey
#monkey.patch_all()

from brad_scene import *

from flask import Flask, session, request, url_for
from flask.ext.socketio import SocketIO, emit, disconnect

import zmq, threading

app = Flask(__name__, static_folder = 'app', static_url_path = '')
app.debug = True
app.config['SECRET_KEY'] = 'no_secrets!'
app.zmqcontext = zmq.Context()
socketio = SocketIO(app)

CHARBRAD = 'ChrBrad'

@socketio.on('update', namespace='/test')
def update_message(message):
    session['receive_count'] = session.get('receive_count', 0) + 1

    #should call brad playguitar or idle based on message[data]
    dtime = message['data']
    sttime = str(dtime)
    print "update received - " + sttime

    socket = app.zmqcontext.socket(zmq.REQ)
    socket.connect("inproc://frontend")
    socket.send_multipart([b"update", sttime])
    resp = socket.recv()
    socket.close()

    #update_scene_dt(float(dtime))
    #char = reply#get_character_bonedata(CHARBRAD)
    emit('bone update',
         {'data': resp, 'count': session['receive_count']})

@socketio.on('play bml', namespace='/test')
def play_message(message):
    session['receive_count'] = session.get('receive_count', 0) + 1

    #for example call brad playguitar or idle based on message[data]
    bml_tags = message['data']
    print "play bml received - " + bml_tags

    socket = app.zmqcontext.socket(zmq.REQ)
    socket.connect("inproc://frontend")
    socket.send(b"idle")
    reply = socket.recv()
    socket.close()

@app.route('/')
def index():
    return app.send_static_file('brad_scene.html')


def main():
    ctx = app.zmqcontext
    tprint("Initialize SceneRouterTask...")
    sbSceneRouter = SceneRouterTask(ctx)
    sbSceneRouter.start()

    tprint("Initialize SbSceneWorkerTask...")
    sbSceneWorker = SbSceneWorkerTask(ctx,1)
    sbSceneWorker.start()

    # tprint("Initialize TestSceneClientTask...")
    # sbTestClient = TestSceneClientTask(ctx,20)
    # sbTestClient.start()

    socketio.run(app, port=5050, use_reloader=False)


    #sbSceneRouter.join()
    #sbSceneWorker.join()
    #ctx.term()

if __name__ == "__main__":
    main()
