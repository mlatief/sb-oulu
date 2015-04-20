import os
import sys
# import time
import math
import random

import threading

# import msgpack
import ujson

import zmq

import SmartBody
from SmartBody import SrVec, CharacterListener, SBEventHandler

from sbscripts import zebra2map as z2m
from sbscripts import BehaviorSetMaleLocomotion, BehaviorSetGestures

# from crowddemo import CrowdDemo, LocomotionHandler


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


def vec2str(vec):
    ''' Converts SrVec to string '''
    x = vec.getData(0)
    y = vec.getData(1)
    z = vec.getData(2)
    if -0.0001 < x < 0.0001:
        x = 0
    if -0.0001 < y < 0.0001:
        y = 0
    if -0.0001 < z < 0.0001:
        z = 0
    return "" + str(x) + " " + str(y) + ""


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

bradReached = False


# Locomotion handler to check if characters have arrived
class LocomotionHandler(SBEventHandler):
    def __init__(self):
        self.reachCount = 0
        SBEventHandler.__init__(self)

    def executeAction(self, ev):
        global bradReached
        params = ev.getParameters()
        print("executeAction ...")
        if 'success' in params:
            if 'ChrBrad' in params:
                self.reachCount = self.reachCount + 1
                if self.reachCount >= 6:
                    bradReached = True
                    self.reachCount = 0


class SbSceneWorkerTask(threading.Thread):
    """SbSceneWorkerTask"""
    def __init__(self, id):
        self.id = id
        threading.Thread.__init__(self)

        self.scene = SmartBody.getScene()
        self.assetManager = self.scene.getAssetManager()
        self.bml = self.scene.getBmlProcessor()
        self.sim = self.scene.getSimulationManager()
        self.steerManager = self.scene.getSteerManager()

        self.init_assets()
        self.create_brads()

        self.bradCur = 0
        self.start_simulation()
        # self.animate_brads()

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
        # for i in range(0,len(motionNames)):
        #    print 'motion ' + str(i) + ' = ' + motionNames[i]
        # for i in range(0,len(skelNames)):
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
        row = 0
        column = 0
        offsetX = 0
        offsetZ = 0
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
            if i == 0:
                # self.scene.run('BehaviorSetMaleLocomotion.py')
                BehaviorSetMaleLocomotion.setupBehaviorSet(self.scene)
                BehaviorSetMaleLocomotion.retargetBehaviorSet(self.scene,
                                                              baseName)

                # self.scene.run('BehaviorSetGestures.py')
                BehaviorSetGestures.setupBehaviorSet(self.scene)
                # setupBehaviorSet()
                BehaviorSetGestures.retargetBehaviorSet(self.scene, baseName)

            steerAgent = self.steerManager.createSteerAgent(baseName)
            steerAgent.setSteerStateNamePrefix("all")
            steerAgent.setSteerType("example")
            # Set up steering
            # setupSteerAgent(baseName, 'ChrBrad.sk')
            brad.setBoolAttribute('steering.pathFollowingMode', False)
            # Play default animation
            self.bml.execBML(baseName, '<body posture="ChrBrad@Idle01"/>')

        tprint('SB: num of characters in the scene = ' +
               str(self.scene.getNumCharacters()))

        self.steerManager.setEnable(False)
        self.steerManager.setEnable(True)

        locomotionHdl = LocomotionHandler()
        evtMgr = self.scene.getEventManager()
        evtMgr.addEventHandler('locomotion', locomotionHdl)

    def animate_brads(self):
        bradPath = [SrVec(-8, -8, 0), SrVec(8, 8, 0), SrVec(8, -8, 0),
                    SrVec(-8, 8, 0)]

        bradList = []
        for name in self.scene.getCharacterNames():
            if 'ChrBrad' in name:
                bradList.append(self.scene.getCharacter(name))

        newLocation = vec2str(bradPath[self.bradCur])

        for brad in bradList:
            print("Moving Brad " + brad.getName() + " to " + newLocation)
            # Move character
            self.bml.execBML(brad.getName(),
                             '<locomotion speed="' +
                             str(random.uniform(1.20, 5.0)) +
                             '" target="' +
                             newLocation + '"/>')

        self.bradCur = self.bradCur + 1
        if self.bradCur >= len(bradPath):
            self.bradCur = 0

        # Run the update script
        # self.scene.removeScript('crowddemo')
        # crowddemo = CrowdDemo(self.scene)
        # self.scene.addScript('crowddemo', crowddemo)

    def start_simulation(self):
        self.sim.setTime(0.0)
        self.sim.start()

    def update_scene_dt(self, dt):
        tprint('SB: Update ...')
        self.scene.update()
        self.sim.setTime(self.sim.getTime()+dt)

    def set_zcontext(self, context):
        self.zcontext = context

    def get_character_bonedata(self, cname):
        sbchar = self.scene.getCharacter(cname)
        sbskel = sbchar.getSkeleton()
        mychar = {'name': cname}

        # Character position (SrVec)
        characterPosVec = sbchar.getPosition()
        # Character orientation (SrQuat)
        characterQuat = sbchar.getOrientation()

        mychar['pos'] = SrVecToXYZ(characterPosVec)
        mychar['rot'] = SrQuatToWXYZ(characterQuat)

        numJoints = sbskel.getNumJoints()

        mychar['skeleton'] = []
        numJoints = sbskel.getNumJoints()
        for j in range(numJoints):
            sbjoint = sbskel.getJoint(j)
            jname = sbjoint.getName()
            jpos = sbjoint.getPosition()
            jquat = sbjoint.getQuat()
            j = {"name": jname,
                 "pos": SrVecToXYZ(jpos),
                 "rot": SrQuatToWXYZ(jquat)}
            # mychar["skeleton"].append(j)

        # m = msgpack.packb(mychar)
        m = ujson.dumps(mychar)
        return m

    def run(self):
        print("Starting SBSceneWorker thread...")
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
            if cmd == 'update' and len(request) > 3:
                dt = float(request[3])
                self.update_scene_dt(dt)
            elif cmd == 'get_update' and len(request) > 3:
                charName = request[3]
                response = self.get_character_bonedata(charName)
            elif cmd == 'animate':
                self.animate_brads()
            elif cmd == 'HELLO':
                response = b"HELLO"

            socket.send_multipart([address, b"", response])


class TestSceneClientTask(threading.Thread):
    """SbSceneRouterTask"""
    def __init__(self, context, id):
        self.zcontext = context
        self.id = id
        threading.Thread.__init__(self)

    def run(self):
        context = self.zcontext
        socket = context.socket(zmq.REQ)
        socket.identity = u"TestClient-{}".format(self.id).encode("ascii")
        socket.connect("inproc://frontend")

        # tprint("{}: {}"
        #        .format(socket.identity.decode("ascii"), "Send HELLO"))
        socket.send(b"HELLO")
        reply = socket.recv()
        # tprint("{}: {}"
        #        .format(socket.identity.decode("ascii"),
        #                reply.decode("ascii")))

        socket.send(b"animate")
        reply = socket.recv()

        for i in range(20):
            # tprint("{}: {}"
            #        .format(socket.identity.decode("ascii"),
            #                "Get updates"))
            socket.send_multipart([b"get_update",
                                  ("ChrBrad%s" % i).encode("ascii")])
            reply = socket.recv()
            tprint("{}: {}".format(socket.identity.decode("ascii"), reply))

        for j in range(5):
            socket.send_multipart([b"update", str(0.2)])
            reply = socket.recv()
        #    tprint("{}: {}".format(socket.identity.decode("ascii"), reply))
        # socket.send_multipart([b"update", str(0.2)])
        # reply = socket.recv()
        for i in range(20):
            # tprint("{}: {}"
            #        .format(socket.identity.decode("ascii"), "Get updates"))
            socket.send_multipart([b"get_update",
                                  ("ChrBrad%s" % i).encode("ascii")])
            reply = socket.recv()
            tprint("{}: {}".format(socket.identity.decode("ascii"), reply))


class SceneRouterTask(threading.Thread):
    """SbSceneRouterTask"""
    def __init__(self, context):
        self.zcontext = context
        threading.Thread.__init__(self)

    def run(self):
        print("Starting SceneRouterTask...")
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
                    backend.send_multipart([worker, b"", client, b"",
                                           cmd, request[3]])
                else:
                    backend.send_multipart([worker, b"", client, b"", cmd])
                if not workers:
                    # Don't poll clients if no workers are available
                    poller.unregister(frontend)

        frontend.close()
        backend.close()


def main():
    tprint("Initialize SbSceneWorkerTask...")
    sbSceneWorker = SbSceneWorkerTask(1)
    # sbSceneWorker.start_simulation()

    ctx = zmq.Context()
    sbSceneWorker.set_zcontext(ctx)
    sbSceneWorker.start()

    tprint("Initialize TestSceneClientTask...")
    sbTestClient = TestSceneClientTask(ctx, 1)
    sbTestClient.start()

    tprint("Initialize SceneRouterTask...")
    sbSceneRouter = SceneRouterTask(ctx)
    sbSceneRouter.start()

    sbSceneWorker.join()
    # sbTestClient.join()
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
