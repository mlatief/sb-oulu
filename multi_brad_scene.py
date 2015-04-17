import os, sys
import time, math, random

import threading

import msgpack
import ujson

import zmq

import SmartBody
from SmartBody import *

from sbscripts import zebra2map as z2m
from sbscripts import BehaviorSetMaleLocomotion, BehaviorSetGestures

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
        self.steerManager = self.scene.getSteerManager()

        self.init_assets()
        self.create_brads()

        tprint("Initialized!")


    def init_assets(self):
        self.scene.setMediaPath(os.environ['SmartBodyDir'] + '/data')
        tprint('media path = ' + self.scene.getMediaPath())

        self.assetManager.addAssetPath('mesh', 'mesh')
        self.assetManager.addAssetPath('script', 'scripts')
        self.assetManager.addAssetPath("script", "behaviorsets")
        self.assetManager.addAssetPath('motion', 'ChrBrad')
        self.assetManager.loadAssets()
        self.scene.setScale(1.0)

        motionNames = self.assetManager.getMotionNames()
        skelNames = self.assetManager.getSkeletonNames()
        #for i in range(0,len(motionNames)):
        #    print 'motion ' + str(i) + ' = ' + motionNames[i]
        #for i in range(0,len(skelNames)):
        #    print 'skeleton ' + str(i) + ' = ' + skelNames[i]
        tprint("Loaded motions: " + str(len(motionNames)))
        tprint("Loaded skeletons: " + str(len(skelNames)))


    def create_brads(self):
        z2m.Zebra2map(self.scene)
        zebra2Map = self.scene.getJointMapManager().getJointMap('zebra2')
        bradSkeleton = self.scene.getSkeleton('ChrBrad.sk')
        zebra2Map.applySkeleton(bradSkeleton)
        zebra2Map.applyMotionRecurse('ChrBrad')

        amount = 20
        row = 0; column = 0;
        offsetX = 0; offsetZ = 0;
        for i in range(amount):
            baseName = 'ChrBrad%s' % i
            brad = self.scene.createCharacter(baseName, '')
            bradSkeleton = self.scene.createSkeleton('ChrBrad.sk')
            brad.setSkeleton(bradSkeleton)
            # Set position logic
            posX = (-100 * (5/2)) + 100 * column
            posZ = ((-100 / math.sqrt(amount)) * (amount/2)) + 100 * row
            column = column + 1
            if column >= 5:
                column = 0
                row = row + 1
            bradPos = SrVec((posX + offsetX)/100, 0, (posZ + offsetZ)/100)
            brad.setPosition(bradPos)
            # Set up standard controllers
            brad.createStandardControllers()

            # setup mocap locomotion
            if i== 0 :
                #self.scene.run('BehaviorSetMaleLocomotion.py')
                BehaviorSetMaleLocomotion.setupBehaviorSet(self.scene)
                BehaviorSetMaleLocomotion.retargetBehaviorSet(self.scene, baseName)
                    
                #self.scene.run('BehaviorSetGestures.py')
                BehaviorSetGestures.setupBehaviorSet(self.scene)
                #setupBehaviorSet()
                BehaviorSetGestures.retargetBehaviorSet(self.scene, baseName)

            steerAgent = self.steerManager.createSteerAgent(baseName)
            steerAgent.setSteerStateNamePrefix("all")
            steerAgent.setSteerType("example")
            # Set up steering
            #setupSteerAgent(baseName, 'ChrBrad.sk')
            brad.setBoolAttribute('steering.pathFollowingMode', False)
            # Play default animation
            self.bml.execBML(baseName, '<body posture="ChrBrad@Idle01"/>')

        tprint('SB: num of characters in the scene = ' + str(self.scene.getNumCharacters()))
        
        self.steerManager.setEnable(False)
        self.steerManager.setEnable(True)

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

    #tprint("Initialize TestSceneClientTask...")
    #sbTestClient = TestSceneClientTask(ctx,20)
    #sbTestClient.start()

    tprint("Initialize SceneRouterTask...")
    sbSceneRouter = SceneRouterTask(ctx)
    sbSceneRouter.start()

    sbSceneWorker.join()
    #sbTestClient.join()
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
