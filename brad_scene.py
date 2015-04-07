import os, sys
import time

import threading

import SmartBody
from SmartBody import *

import msgpack
import ujson

import zmq

def tprint(msg):
    """like print, but won't get newlines confused with multiple threads"""
    sys.stdout.write(msg + '\n')
    sys.stdout.flush()

class MyListener(CharacterListener):
    def OnCharacterCreate(self, name, type):
        tprint("Character created...")

    def OnCharacterUpdate(self, name):
        tprint(("Character update {0} ...").format(name))

    def OnPawnCreate(self, name):
        tprint("Pawn created...")

    def OnSimulationUpdate(self):
        tprint("Simulation update...")


def SrVecToXYZ(s):
    #return [round(s.getData(0),2), round(s.getData(1),2), round(s.getData(2),2)]
    #return s.__str__()
    return ("{0:.2f},{1:.2f}, {2:.2f}").format(s.getData(0), s.getData(1), s.getData(2))

def SrQuatToWXYZ(s):
    #return s.__str__()
    #return [round(s.getData(0),2), round(s.getData(1),2), round(s.getData(2),2), round(s.getData(3), 2)]
    return ("{0:.2f},{1:.2f},{2:.2f},{3:.2f}").format(s.getData(0), s.getData(1), s.getData(2), s.getData(3))

class SbSceneWorkerTask(threading.Thread):
    """SbSceneWorkerTask"""
    def __init__(self, context, id):
        self.zcontext = context
        self.id = id
        threading.Thread.__init__ (self)

        self.scene = SmartBody.getScene()
        self.assetManager = self.scene.getAssetManager()
        self.bml = self.scene.getBmlProcessor()
        self.sim = self.scene.getSimulationManager()

        self.init_assets()
        self.init_scene()

        tprint("Initialized!")


    def init_assets(self):
        self.scene.setMediaPath(os.environ['SmartBodyDir'] + '/data')
        tprint('media path = ' + self.scene.getMediaPath())

        self.assetManager.addAssetPath('motion', 'ChrBrad')
        self.assetManager.addAssetPath('mesh', 'mesh')
        self.assetManager.addAssetPath('script', 'scripts')
        self.assetManager.loadAssets()

        motionNames = self.assetManager.getMotionNames()
        skelNames = self.assetManager.getSkeletonNames()
        #for i in range(0,len(motionNames)):
        #    print 'motion ' + str(i) + ' = ' + motionNames[i]
        #for i in range(0,len(skelNames)):
        #    print 'skeleton ' + str(i) + ' = ' + skelNames[i]
        tprint("Loaded motions: " + str(len(motionNames)))
        tprint("Loaded skeletons: " + str(len(skelNames)))


    def init_scene(self):
        obj = self.scene.createPawn('obj1')
        obj.setStringAttribute('collisionShape','box')
        obj.setVec3Attribute('collisionShapeScale',5.0,10.0,3.0)

        obj.setPosition(SrVec(0,30,0))
        obj.setHPR(SrVec(0,0,90))

        # set the scene scale and reset the camera
        self.scene.setScale(1.0)
        #scene.getActiveCamera().reset()

        #self.mylistener = MyListener()
        #self.scene.addSceneListener(self.mylistener)

        #self.scene.run('zebra2-map.py')
        self.Zebra2map()
        zebra2Map = self.scene.getJointMapManager().getJointMap('zebra2')
        bradSkeleton = self.scene.getSkeleton('ChrBrad.sk')
        zebra2Map.applySkeleton(bradSkeleton)
        zebra2Map.applyMotionRecurse('ChrBrad')

        # Set up Brad
        brad = self.scene.createCharacter('ChrBrad', '')
        bradSkeleton = self.scene.createSkeleton('ChrBrad.sk')
        brad.setSkeleton(bradSkeleton)
        # Set standard controller
        brad.createStandardControllers()

        #brad.setDoubleAttribute('deformableMeshScale', .01)
        #brad.setStringAttribute('deformableMesh', 'ChrBrad.dae')
        # show the character
        #brad.setStringAttribute('displayType', 'GPUmesh')
        self.bml_idle()
        self.start_simulation()

        tprint('SB: num of pawns in the scene = ' + str(self.scene.getNumPawns()))
        tprint('SB: num of characters in the scene = ' + str(self.scene.getNumCharacters()))


    def Zebra2map(self):

        # Mapping from Zebra2 skeleton to SmartBody skeleton

        jointMapManager = self.scene.getJointMapManager()
        zebra2Map = jointMapManager.getJointMap("zebra2")
        if (zebra2Map == None):
    	       zebra2Map = jointMapManager.createJointMap('zebra2')

        # Core
        zebra2Map.setMapping("JtRoot", "base")
        zebra2Map.setMapping("JtSpineA", "spine1")
        zebra2Map.setMapping("JtSpineB", "spine2")
        zebra2Map.setMapping("JtSpineC", "spine3")
        zebra2Map.setMapping("JtNeckA", "spine4")
        zebra2Map.setMapping("JtNeckB", "spine5")
        zebra2Map.setMapping("JtSkullA", "skullbase")

        # Arm, left
        zebra2Map.setMapping("JtClavicleLf", "l_sternoclavicular")
        zebra2Map.setMapping("JtShoulderLf", "l_shoulder")
        zebra2Map.setMapping("JtUpperArmTwistALf", "l_upperarm1")
        zebra2Map.setMapping("JtUpperArmTwistBLf", "l_upperarm2")
        zebra2Map.setMapping("JtElbowLf", "l_elbow")
        zebra2Map.setMapping("JtForearmTwistALf", "l_forearm1")
        zebra2Map.setMapping("JtForearmTwistBLf", "l_forearm2")
        zebra2Map.setMapping("JtWristLf", "l_wrist")
        zebra2Map.setMapping("JtThumbALf", "l_thumb1")
        zebra2Map.setMapping("JtThumbBLf", "l_thumb2")
        zebra2Map.setMapping("JtThumbCLf", "l_thumb3")
        zebra2Map.setMapping("JtThumbDLf", "l_thumb4")
        zebra2Map.setMapping("JtIndexALf", "l_index1")
        zebra2Map.setMapping("JtIndexBLf", "l_index2")
        zebra2Map.setMapping("JtIndexCLf", "l_index3")
        zebra2Map.setMapping("JtIndexDLf", "l_index4")
        zebra2Map.setMapping("JtMiddleALf", "l_middle1")
        zebra2Map.setMapping("JtMiddleBLf", "l_middle2")
        zebra2Map.setMapping("JtMiddleCLf", "l_middle3")
        zebra2Map.setMapping("JtMiddleDLf", "l_middle4")
        zebra2Map.setMapping("JtRingALf", "l_ring1")
        zebra2Map.setMapping("JtRingBLf", "l_ring2")
        zebra2Map.setMapping("JtRingCLf", "l_ring3")
        zebra2Map.setMapping("JtRingDLf", "l_ring4")
        zebra2Map.setMapping("JtLittleALf", "l_pinky1")
        zebra2Map.setMapping("JtLittleBLf", "l_pinky2")
        zebra2Map.setMapping("JtLittleCLf", "l_pinky3")
        zebra2Map.setMapping("JtLittleDLf", "l_pinky4")

        # Arm, right
        zebra2Map.setMapping("JtClavicleRt", "r_sternoclavicular")
        zebra2Map.setMapping("JtShoulderRt", "r_shoulder")
        zebra2Map.setMapping("JtUpperArmTwistARt", "r_upperarm1")
        zebra2Map.setMapping("JtUpperArmTwistBRt", "r_upperarm2")
        zebra2Map.setMapping("JtElbowRt", "r_elbow")
        zebra2Map.setMapping("JtForearmTwistARt", "r_forearm1")
        zebra2Map.setMapping("JtForearmTwistBRt", "r_forearm2")
        zebra2Map.setMapping("JtWristRt", "r_wrist")
        zebra2Map.setMapping("JtThumbARt", "r_thumb1")
        zebra2Map.setMapping("JtThumbBRt", "r_thumb2")
        zebra2Map.setMapping("JtThumbCRt", "r_thumb3")
        zebra2Map.setMapping("JtThumbDRt", "r_thumb4")
        zebra2Map.setMapping("JtIndexARt", "r_index1")
        zebra2Map.setMapping("JtIndexBRt", "r_index2")
        zebra2Map.setMapping("JtIndexCRt", "r_index3")
        zebra2Map.setMapping("JtIndexDRt", "r_index4")
        zebra2Map.setMapping("JtMiddleARt", "r_middle1")
        zebra2Map.setMapping("JtMiddleBRt", "r_middle2")
        zebra2Map.setMapping("JtMiddleCRt", "r_middle3")
        zebra2Map.setMapping("JtMiddleDRt", "r_middle4")
        zebra2Map.setMapping("JtRingARt", "r_ring1")
        zebra2Map.setMapping("JtRingBRt", "r_ring2")
        zebra2Map.setMapping("JtRingCRt", "r_ring3")
        zebra2Map.setMapping("JtRingDRt", "r_ring4")
        zebra2Map.setMapping("JtLittleARt", "r_pinky1")
        zebra2Map.setMapping("JtLittleBRt", "r_pinky2")
        zebra2Map.setMapping("JtLittleCRt", "r_pinky3")
        zebra2Map.setMapping("JtLittleDRt", "r_pinky4")

        # Leg, left
        zebra2Map.setMapping("JtHipLf", "l_hip")
        zebra2Map.setMapping("JtKneeLf", "l_knee")
        zebra2Map.setMapping("JtAnkleLf", "l_ankle")
        zebra2Map.setMapping("JtBallLf", "l_forefoot")
        zebra2Map.setMapping("JtToeLf", "l_toe")

        # Leg, right
        zebra2Map.setMapping("JtHipRt", "r_hip")
        zebra2Map.setMapping("JtKneeRt", "r_knee")
        zebra2Map.setMapping("JtAnkleRt", "r_ankle")
        zebra2Map.setMapping("JtBallRt", "r_forefoot")
        zebra2Map.setMapping("JtToeRt", "r_toe")

        # Head, left
        zebra2Map.setMapping("JtEyeLf", "eyeball_left")
        zebra2Map.setMapping("JtEyelidUpperLf", "upper_eyelid_left")
        zebra2Map.setMapping("JtEyelidLowerLf", "lower_eyelid_left")

        # Head, right
        zebra2Map.setMapping("JtEyeRt", "eyeball_right")
        zebra2Map.setMapping("JtEyelidUpperRt", "upper_eyelid_right")
        zebra2Map.setMapping("JtEyelidLowerRt", "lower_eyelid_right")

        #zebra2Map.setMapping("eyeJoint_R", "eyeball_right")
        #zebra2Map.setMapping("eyeJoint_L", "eyeball_left")


    def start_simulation(self):
        self.sim.setTime(0.0)
        self.sim.start()

    def play_bml(self,character, bml_tags):
        self.bml.execBML(character, bml_tags)

    def bml_idle(self):
        tprint('SB: BML idle ...')
        self.bml.execBML('ChrBrad', '<body posture="ChrBrad@Idle01"/>')

    def bml_guitar(self):
        tprint( 'SB: BML guitar ...')
        self.bml.execBML('ChrBrad', '<body posture="ChrBrad@Guitar01"/>')

    def update_scene_dt(self, dt):
        tprint( 'SB: Update scene ...')
        self.scene.update()
        self.sim.setTime(self.sim.getTime()+dt)


    def get_character_bonedata(self, cname):
        sbchar = self.scene.getCharacter(cname)
        sbskel = sbchar.getSkeleton()
        mychar = {'name': cname}

        # global position (SrVec)
        globalPosVec = sbchar.getPosition()
        # global orientation
        globalQuat = sbchar.getOrientation()

        mychar['pos'] = SrVecToXYZ(globalPosVec)
        mychar['rot'] = SrQuatToWXYZ(globalQuat)

        #curLen = len(mychar['skeleton'])
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
            jname = sbjoint.getName()
            jpos = sbjoint.getPosition()
            jquat = sbjoint.getQuat()
            j = { "name": jname, "pos": SrVecToXYZ(jpos), "rot": SrQuatToWXYZ(jquat)}
            mychar["skeleton"].append(j)

        #m = msgpack.packb(mychar)
        m = ujson.dumps(mychar)
        return m


    def run(self):
        context = self.zcontext
        socket = context.socket(zmq.REQ)
        identity = u"Worker-{}".format(self.id)
        socket.identity = identity.encode('ascii')
        socket.connect('inproc://backend')

        tprint("{}: {}".format(socket.identity.decode("ascii"), "Send READY"))
        socket.send(b"READY")
        while True:
            request = socket.recv_multipart()
            address, empty, cmd = request[:3]
            tprint("{}: {}".format(socket.identity.decode("ascii"),
                                  cmd.decode("ascii")))
            response = b"OK"
            if cmd == 'update' and len(request)>3:
                self.update_scene_dt(float(request[3]))
                response = self.get_character_bonedata("ChrBrad")
            elif cmd == 'bml' and len(request)>3:
                self.play_bml(request[3])
            elif cmd=='idle':
                self.bml_idle()
            elif cmd == 'guitar':
                self.bml_guitar()
            elif cmd == 'HELLO':
                response = b"HELLO"

            socket.send_multipart([address, b"", response])


class TestSceneClientTask(threading.Thread):
    """SbSceneRouterTask"""
    def __init__(self, context, id):
        self.zcontext = context
        self.id = id
        threading.Thread.__init__ (self)

    def run(self):
        context = self.zcontext
        socket = context.socket(zmq.REQ)
        socket.identity = u"TestClient-{}".format(self.id).encode("ascii")
        socket.connect("inproc://frontend")

        tprint("{}: {}".format(socket.identity.decode("ascii"), "Send HELLO"))
        socket.send(b"HELLO")
        reply = socket.recv()
        tprint("{}: {}".format(socket.identity.decode("ascii"), reply.decode("ascii")))

        tprint("{}: {}".format(socket.identity.decode("ascii"), "Send idle"))
        socket.send(b"idle")
        reply = socket.recv()
        tprint("{}: {}".format(socket.identity.decode("ascii"), reply.decode("ascii")))

        for i in range(100):
            tprint("{}: {}".format(socket.identity.decode("ascii"), "Send Update"))
            socket.send_multipart([b"update", str(0.016)])
            reply = socket.recv()
            tprint("{}: {}".format(socket.identity.decode("ascii"), reply))

class SceneRouterTask(threading.Thread):
    """SbSceneRouterTask"""
    def __init__(self, context):
        self.zcontext = context
        threading.Thread.__init__ (self)

    def run(self):
        context = self.zcontext
        frontend = context.socket(zmq.ROUTER)
        frontend.bind("inproc://frontend")

        backend = context.socket(zmq.ROUTER)
        backend.bind("inproc://backend")

        workers = []
        poller = zmq.Poller()
        # Only poll for requests from backend until workers are available
        poller.register(backend, zmq.POLLIN)
        while True:
            tprint("Polling for connections...")
            sockets = dict(poller.poll())
            if backend in sockets:
                # Handle worker activity on the backend
                request = backend.recv_multipart()
                worker, empty, client = request[:3]
                if not workers:
                    poller.register(frontend, zmq.POLLIN)
                workers.append(worker)
                if client != b"READY" and len(request) > 3:
                    # If client reply, send rest back to frontend
                    empty, reply = request[3:]
                    frontend.send_multipart([client, b"", reply])

            if frontend in sockets:
                # Get next client request, route to last-used worker
                request = frontend.recv_multipart()
                client, empty, cmd = request[:3]
                worker = workers.pop(0)
                if len(request) > 3:
                    backend.send_multipart([worker, b"", client, b"", cmd, request[3] ])
                else:
                    backend.send_multipart([worker, b"", client, b"", cmd])
                if not workers:
                    # Don't poll clients if no workers are available
                    poller.unregister(frontend)

        frontend.close()
        backend.close()

def main():
    ctx = zmq.Context()
    tprint("Initialize SbSceneWorkerTask...")
    sbSceneWorker = SbSceneWorkerTask(ctx,1)
    sbSceneWorker.start()

    tprint("Initialize TestSceneClientTask...")
    sbTestClient = TestSceneClientTask(ctx,20)
    sbTestClient.start()

    tprint("Initialize SceneRouterTask...")
    sbSceneRouter = SceneRouterTask(ctx)
    sbSceneRouter.start()

    sbSceneWorker.join()
    sbTestClient.join()
    sbSceneRouter.join()
    ctx.term()

if __name__ == "__main__":
    main()
    # bml_idle()
    # start_simulation()
    # while(sim.getTime()<100):
    #     print ("### before update {0:.2f} ..").format(sim.getTime())
    #     scene.update()
    #
    #     print "### before setTime(getTime).."
    #     sim.setTime(sim.getTime()+0.16)
    #
    #     #logging.info("Simulation is at time: " + str(sim.getTime()))
    #     print "### before get.."
    #     c = get_character_bonedata("ChrBrad")
    #     print ("Returned dictionary of size: {0:d}").format(sys.getsizeof(c))
    #     print ("Returned string: {0}").format(c)
    #
    # print "### Stop simulation.."
    # sim.stop()
