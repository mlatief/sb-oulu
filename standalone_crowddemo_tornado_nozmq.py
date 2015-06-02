import os
import sys
import time

import SmartBody
from SmartBody import *

import ujson

import tornado
from tornado import websocket, web, ioloop

from app_settings import settings, zmq_router_fe, ws_tcp_port, zmq_router_be

def tprint(msg):
    """like print, but won't get newlines confused with multiple threads"""
    sys.stdout.write(msg + '\n')
    sys.stdout.flush()

scene = SmartBody.getScene()
bml = scene.getBmlProcessor()
assetManager = scene.getAssetManager()

scene.startFileLogging("smartbody.log");

scene.setMediaPath(os.environ['SmartBodyDir'] + '/data')
tprint('media path = ' + scene.getMediaPath())

assetManager.addAssetPath("script", "scripts")
assetManager.addAssetPath("script", "my")
assetManager.loadAssets()

scene.run("CrowdDemo.py")

tprint("Script loaded!")

startTime = time.clock()

def SrVecToXYZ(s):
    return ("{0:.2f},{1:.2f},{2:.2f}").format(s.getData(0), s.getData(1), s.getData(2))


def SrQuatToWXYZ(s):
    return ("{0:.2f},{1:.2f},{2:.2f},{3:.2f}").format(s.getData(0), s.getData(1), s.getData(2), s.getData(3))

def get_characters_bonedata():
    bradList = scene.getCharacterNames()
    num = len(bradList)
    print("...number of characters %d" % num)
    characters = []
    for bradName in bradList:
        mychar = {'name': bradName}
        sbchar = scene.getCharacter(bradName)
        sbskel = sbchar.getSkeleton()

        # global position (SrVec)
        globalPosVec = sbchar.getPosition()
        # global orientation
        globalQuat = sbchar.getOrientation()
        mychar['pos'] = SrVecToXYZ(globalPosVec)
        mychar['rot'] = SrQuatToWXYZ(globalQuat)
        mychar['skeleton'] = []
        numJoints = sbskel.getNumJoints()
        for j in range(numJoints):
            sbjoint = sbskel.getJoint(j)
            jname = sbjoint.getName()
            jpos = sbjoint.getPosition()
            jquat = sbjoint.getQuat()
            j = { 'name': jname, 'pos': SrVecToXYZ(jpos), 'rot': SrQuatToWXYZ(jquat)}
            #mychar['skeleton'].append(j)

        characters.append(mychar)

    m = ujson.dumps(characters)
    return m


sim = scene.getSimulationManager();
sim.setTime(0.0)
sim.start()

def updateScene():
    bradList = scene.getCharacterNames()
    num = len(bradList)
    tprint("...number of characters %d" % num)
    for bradName in bradList:
        char = scene.getCharacter(bradName)
        pos = char.getPosition()
        quat = char.getOrientation()

        tprint("Character %s, pos: %s, quat: %s" %
               (bradName, SrVecToXYZ(pos), SrQuatToWXYZ(quat)))

class IndexHandler(web.RequestHandler):
    def get(self):
        self.render("app\\multi_brad_scene.html")

class SocketHandler(websocket.WebSocketHandler):
    def check_origin(self, origin):
        return True

    def open(self):
        print("...WebSocket opened!")

    def on_close(self):
        print("WebSocket closed")

    def on_message(self, message):
        print("Received: " + message)
        m = ujson.loads(message)
        cmd = m['command']
        print("...Command: " + cmd)
        if cmd=='update':
            #dtime = str(m['data'])
            scene.update()
            sim.setTime(sim.getTime()+0.1)
            updateScene()
            #self.write_message(get_characters_bonedata())



app = web.Application([
    (r'/', IndexHandler),
    (r'/ws', SocketHandler),
    (r'/js/(.*)',web.StaticFileHandler, {'path': './app/js'},),
    (r'/models/(.*)',web.StaticFileHandler, {'path': './app/models'},)
], **settings)

if __name__ == '__main__':
    app.listen(ws_tcp_port)
    print ("Listening on %d..." % ws_tcp_port)

    try:
        ioloop.IOLoop.instance().start()
    except KeyboardInterrupt:
        print ('Interrupted')



