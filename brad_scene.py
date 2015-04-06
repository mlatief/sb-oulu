import os, sys
import time
import SmartBody
from SmartBody import *

import msgpack
import ujson

scene = SmartBody.getScene()
assetManager = scene.getAssetManager()
bml = scene.getBmlProcessor()
sim = scene.getSimulationManager()

mychar_buffer = {'name': '', 'pos':[], 'rot':[], 'skeleton': [{}]*122}

class MyListener(CharacterListener):
    def OnCharacterCreate(self, name, type):
        print "Character created..."

    def OnCharacterUpdate(self, name):
        print ("Character update {0} ...").format(name)

    def OnPawnCreate(self, name):
        print "Pawn created..."

    def OnSimulationUpdate(self):
        print "Simulation update..."

def init_assets():
    scene.setMediaPath(os.environ['SmartBodyDir'] + '/data')
    print 'media path = ' + scene.getMediaPath()

    assetManager.addAssetPath('motion', 'ChrBrad')
    assetManager.addAssetPath('mesh', 'mesh')
    assetManager.addAssetPath('script', 'scripts')
    assetManager.loadAssets()

    motionNames = assetManager.getMotionNames()
    skelNames = assetManager.getSkeletonNames()
    #for i in range(0,len(motionNames)):
    #    print 'motion ' + str(i) + ' = ' + motionNames[i]
    #for i in range(0,len(skelNames)):
    #    print 'skeleton ' + str(i) + ' = ' + skelNames[i]
    print "Loaded motions: " + str(len(motionNames))
    print "Loaded skeletons: " + str(len(skelNames))


def init_scene():
    obj = scene.createPawn('obj1')
    obj.setStringAttribute('collisionShape','box')
    obj.setVec3Attribute('collisionShapeScale',5.0,10.0,3.0)

    obj.setPosition(SrVec(0,30,0))
    obj.setHPR(SrVec(0,0,90))

    # set the scene scale and reset the camera
    scene.setScale(1.0)
    #scene.getActiveCamera().reset()

    mylistener = MyListener()
    scene.addSceneListener(mylistener)

    scene.run('zebra2-map.py')
    zebra2Map = scene.getJointMapManager().getJointMap('zebra2')
    bradSkeleton = scene.getSkeleton('ChrBrad.sk')
    zebra2Map.applySkeleton(bradSkeleton)
    zebra2Map.applyMotionRecurse('ChrBrad')

    # Set up Brad
    brad = scene.createCharacter('ChrBrad', '')
    bradSkeleton = scene.createSkeleton('ChrBrad.sk')
    brad.setSkeleton(bradSkeleton)
    # Set standard controller
    brad.createStandardControllers()

    #brad.setDoubleAttribute('deformableMeshScale', .01)
    #brad.setStringAttribute('deformableMesh', 'ChrBrad.dae')
    # show the character
    #brad.setStringAttribute('displayType', 'GPUmesh')

    print 'num of pawns in the scene = ' + str(scene.getNumPawns())
    print 'num of characters in the scene = ' + str(scene.getNumCharacters())

def bml_idle():
    print 'BML idle ...'
    bml.execBML('ChrBrad', '<body posture="ChrBrad@Idle01"/>')

def bml_guitar():
    print 'BML guitar ...'
    bml.execBML('ChrBrad', '<body posture="ChrBrad@Guitar01"/>')

def start_simulation():
    sim.setTime(0.0)
    sim.start()

def update_scene(t):
    scene.update()
    sim.setTime(t)

def SrVecToXYZ(s):
    #return [round(s.getData(0),2), round(s.getData(1),2), round(s.getData(2),2)]
    return s.__str__()
    #return ("{0:.2f},{1:.2f}, {2:.2f}").format(s.getData(0), s.getData(1), s.getData(2))

def SrQuatToWXYZ(s):
    #return s.__str__()
    #return [round(s.getData(0),2), round(s.getData(1),2), round(s.getData(2),2), round(s.getData(3), 2)]
    return ("{0:.2f},{1:.2f},{2:.2f},{3:.2f}").format(s.getData(0), s.getData(1), s.getData(2), s.getData(3))

def get_character(cname):
    sbchar = scene.getCharacter(cname)
    sbskel = sbchar.getSkeleton()
    mychar = {'name': cname}

    # global position (SrVec)
    globalPosVec = sbchar.getPosition()
    # global orientation
    globalQuat = sbchar.getOrientation()

    mychar['pos'] = SrVecToXYZ(globalPosVec)
    mychar['rot'] = SrQuatToWXYZ(globalQuat)

    curLen = len(mychar_buffer['skeleton'])
    numJoints = sbskel.getNumJoints()

    # joint_name = "JtRoot"
    # sbrootjoint = sbskel.getJointByName("JtRoot")
    # if(sbrootjoint):
    #     pos = sbrootjoint.getPosition()
    #     mychar_buffer["skeleton"][0]['name'] = "JtRoot"
    #     mychar_buffer["skeleton"][0]['position'] = pos.__str__
    mychar['skeleton'] = [{}]
    numJoints = sbskel.getNumJoints()
    for j in range(numJoints):
        sbjoint = sbskel.getJoint(j)
        #jname=""
        jname = sbjoint.getName()
        jpos = sbjoint.getPosition()
        jquat = sbjoint.getQuat()
        j = { "name": jname, "pos": SrVecToXYZ(jpos), "rot": SrQuatToWXYZ(jquat)}
        mychar["skeleton"].append(j)

    m = msgpack.packb(mychar)
    #m=ujson.dumps(mychar)
    return m

if __name__ == "__main__":
    init_assets()
    init_scene()

    bml_idle()
    start_simulation()
    while(sim.getTime()<100):
        print ("### before update {0:.2f} ..").format(sim.getTime())
        scene.update()

        print "### before setTime(getTime).."
        sim.setTime(sim.getTime()+0.16)

        #logging.info("Simulation is at time: " + str(sim.getTime()))
        print "### before get.."
        c = get_character("ChrBrad")
        print ("Returned dictionary of size: {0:d}").format(sys.getsizeof(c))
        print ("Returned string: {0}").format(c)


    sim.stop()
