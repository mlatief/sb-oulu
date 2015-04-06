from gevent import monkey
monkey.patch_all()

from brad_scene import *

from flask import Flask, session, request, url_for
from flask.ext.socketio import SocketIO, emit, disconnect

app = Flask(__name__, static_folder = 'app', static_url_path = '')
app.debug = True
app.config['SECRET_KEY'] = 'no_secrets!'
socketio = SocketIO(app)

@socketio.on('update', namespace='/test')
def test_message(message):
    session['receive_count'] = session.get('receive_count', 0) + 1

    #should call brad playguitar or idle based on message[data]
    dtime = message['data']

    update_scene(float(dtime))
    char = get_character('ChrBrad')
    emit('bone update',
         {'data': char, 'count': session['receive_count']})

@socketio.on('play bml', namespace='/test')
def test_message(message):
    session['receive_count'] = session.get('receive_count', 0) + 1

    #should call brad playguitar or idle based on message[data]
    action = message['data']
    if action == 'idle':
        bml_idle()
    else if action == 'guitar'
        bml_guitar()

@app.route('/')
def index():
    return app.send_static_file('brad_scene.html')

if __name__ == "__main__":
    init_assets()
    init_scene()
    socketio.run(app, port=5050, use_reloader=False)
