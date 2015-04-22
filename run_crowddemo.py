import os
import sys
import time

#import ujson

import SmartBody
#from SmartBody import StringVec, DoubleVec, SrVec, CharacterListener
from SmartBody import *

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
    # return [round(s.getData(0),2), round(s.getData(1),2),
    # round(s.getData(2),2)]
    # return s.__str__()
    return ("{0:.2f},{1:.2f},{2:.2f}").format(s.getData(0), s.getData(1), s.getData(2))


def SrQuatToWXYZ(s):
    # return s.__str__()
    # return [round(s.getData(0),2), round(s.getData(1),2), round(s.\
    # getData(2),2), round(s.getData(3), 2)]
    return ("{0:.2f},{1:.2f},{2:.2f},{3:.2f}").format(s.getData(0), s.getData(1), s.getData(2), s.getData(3))

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

sim = scene.getSimulationManager();
sim.setTime(0.0)
sim.start()

while True:
    beginningTime = time.clock()

    elapsed = beginningTime - startTime

    scene.update()
    sim.setTime(sim.getTime()+0.1)

    updateScene()

    time.sleep(0.1)

