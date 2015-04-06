import zmq

import os, sys
import threading
import time

def tprint(msg):
    """like print, but won't get newlines confused with multiple threads"""
    sys.stdout.write(msg + '\n')
    sys.stdout.flush()

class SbSceneWorkerTask(threading.Thread):
    """SbSceneWorkerTask"""
    def __init__(self, context, id):
        self.zcontext = context
        self.id = id
        threading.Thread.__init__ (self)

    def run(self):
        context = self.zcontext #zmq.Context()
        socket = context.socket(zmq.REQ)
        identity = u"Worker-{}".format(self.id)
        socket.identity = identity.encode('ascii')
        #socket.connect("tcp://localhost:5557")
        socket.connect("inproc://backend")

        tprint("{}: {}".format(socket.identity.decode("ascii"), "Send READY"))
        socket.send_string(b"READY")
        while True:
            address, empty, request = socket.recv_multipart()
            tprint("{}: {}".format(socket.identity.decode("ascii"),
                                  request.decode("ascii")))
            response = b"OK"
            if request=='idle':
                self.bml_idle()
            elif request == 'guitar':
                self.bml_guitar()
            elif request == 'update':
                self.update_scene_dt(0.1)
            elif request == 'HELLO':
                response = b"HELLO"

            socket.send_multipart([address, b"", response])


class TestSceneClientTask(threading.Thread):
    """TestSceneClientTask"""
    def __init__(self, context, id):
        self.zcontext = context
        self.id = id
        threading.Thread.__init__ (self)

    def run(self):
        context = self.zcontext #zmq.Context()
        socket = context.socket(zmq.REQ)
        socket.identity = u"TestClient-{}".format(self.id).encode("ascii")
        #socket.connect("tcp://localhost:5556")
        socket.connect("inproc://frontend")

        tprint("{}: {}".format(socket.identity.decode("ascii"), "Send HELLO"))
        socket.send(b"HELLO")
        reply = socket.recv()
        tprint(">{}: {}".format(socket.identity.decode("ascii"), reply.decode("ascii")))

        tprint("{}: {}".format(socket.identity.decode("ascii"), "Send idle"))
        socket.send_string(b"idle")
        reply = socket.recv()
        tprint(">{}: {}".format(socket.identity.decode("ascii"), reply.decode("ascii")))

        tprint("{}: {}".format(socket.identity.decode("ascii"), "Send Update"))
        socket.send_string(b"update")
        reply = socket.recv()
        tprint(">{}: {}".format(socket.identity.decode("ascii"), reply.decode("ascii")))

class SceneRouterTask(threading.Thread):
    """SceneRouterTask"""
    def __init__(self, context):
        self.zcontext = context
        threading.Thread.__init__ (self)

    def run(self):
        context = self.zcontext #zmq.Context()
        frontend = context.socket(zmq.ROUTER)
        frontend.bind("inproc://frontend")
        #frontend.bind("tcp://*:5556")
        backend = context.socket(zmq.ROUTER)
        #backend.bind("tcp://*:5557")
        backend.bind("inproc://backend")

        tprint("Initialize SbSceneWorkerTask...")
        sbSceneWorker = SbSceneWorkerTask(context, 1)
        sbSceneWorker.start()

        workers = []
        count = 3
        poller = zmq.Poller()
        # Only poll for requests from backend until workers are available
        poller.register(backend, zmq.POLLIN)
        while True:
            tprint( "Polling for connections...")
            try:
                sockets = dict(poller.poll())
            except KeyboardInterrupt:
                break

            if backend in sockets:
                # Handle worker activity on the backend
                request = backend.recv_multipart()
                worker, emp, client = request[:3]
                if not workers:
                    poller.register(frontend, zmq.POLLIN)
                workers.append(worker)
                if client != b"READY" and len(request) > 3:
                    # If client reply, send rest back to frontend
                    empty, reply = request[3:]
                    frontend.send_multipart([client, b"", reply])
                    count -= 1
                    if not count:
                        break

            if frontend in sockets:
                # Get next client request, route to last-used worker
                client, empty, request = frontend.recv_multipart()
                worker = workers.pop(0)
                backend.send_multipart([worker, b"", client, b"", request])
                if not workers:
                    # Don't poll clients if no workers are available
                    poller.unregister(frontend)

        frontend.close()
        backend.close()
        context.term()

def main():
    ctx = zmq.Context()
    sbRouter = SceneRouterTask(ctx)
    sbRouter.start()

    tprint("Initialize TestSceneClientTask...")
    sbTestClient = TestSceneClientTask(ctx, 20)
    sbTestClient.start()

    sbRouter.join()

if __name__ == "__main__":
    main()
