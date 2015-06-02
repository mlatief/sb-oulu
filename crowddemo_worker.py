import os
import sys
import time
import ujson
from app_settings import zmq_router_be

import zmq
from zmq.eventloop import ioloop, zmqstream
ioloop.install()

def tprint(msg):
    """like print, but won't get newlines confused with multiple threads"""
    sys.stdout.write(msg + '\n')
    sys.stdout.flush()

ctx = zmq.Context()
s = ctx.socket(zmq.REQ)
identity = u"Worker-{}".format(1)
s.identity = identity.encode('ascii')
s.connect("tcp://127.0.0.1:%d" % zmq_router_be)
stream = zmqstream.ZMQStream(s)
def printer(msg):
	print(msg)
stream.on_recv(printer)

import SmartBody
from SmartBody import *

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
sim = scene.getSimulationManager();
sim.setTime(0.0)
sim.start()

def SrVecToXYZ(s):
    return ("{0:.2f},{1:.2f},{2:.2f}").format(s.getData(0), s.getData(1), s.getData(2))

def SrQuatToWXYZ(s):
    return ("{0:.2f},{1:.2f},{2:.2f},{3:.2f}").format(s.getData(0), s.getData(1), s.getData(2), s.getData(3))

def printScene():
    bradList = scene.getCharacterNames()
    num = len(bradList)
    tprint("...number of characters %d" % num)
    for bradName in bradList:
        char = scene.getCharacter(bradName)
        pos = char.getPosition()
        quat = char.getOrientation()

        tprint("Character %s, pos: %s, quat: %s" %
               (bradName, SrVecToXYZ(pos), SrQuatToWXYZ(quat)))

def get_characters_bonedata():
    bradList = scene.getCharacterNames()
    num = len(bradList)
    tprint("...number of characters %d" % num)
    characters = []
    for bradName in bradList[:1]:
        mychar = {'name': bradName}
        sbchar = scene.getCharacter(bradName)
        sbskel = sbchar.getSkeleton()

        globalPosVec = sbchar.getPosition()
        globalQuat = sbchar.getOrientation()
        mychar['pos'] = SrVecToXYZ(globalPosVec)
        mychar['rot'] = SrQuatToWXYZ(globalQuat)
        mychar['skeleton'] = []
        numJoints = sbskel.getNumJoints()
        for j in range(numJoints):
            sbjoint = sbskel.getJoint(j)
            jname = sbjoint.getName()
            #if jname=='JtCalvicleLf' or jname=='JtShoulderLf' or jname=='JtCalvicleRt' or jname=='JtShoulderRt':
            jpos = sbjoint.getPosition()
            jquat = sbjoint.getQuat()
            j = { 'name': jname, 'pos': SrVecToXYZ(jpos), 'rot': SrQuatToWXYZ(jquat)}
            mychar['skeleton'].append(j)
        characters.append(mychar)
    m = ujson.dumps(characters)
    return m

def updateScene(request):
    address, empty, cmd = request[:3]
    tprint("{}: {}".format(s.identity.decode("ascii"),
                          cmd.decode("ascii")))
    response = b"OK"
    if cmd == 'update' and len(request)>3:
		scene.update()
		dt = float(request[3])
		sim.setTime(sim.getTime()+dt)
		printScene()
		response = get_characters_bonedata()
    elif cmd == 'HELLO':
        response = b"HELLO"

    stream.send_multipart([address, b"", response])

stream.on_recv(updateScene)
stream.send(b'READY')
print("Worker READY, connected to port: %s" % zmq_router_be)
ioloop.IOLoop.instance().start()
