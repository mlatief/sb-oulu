import zmq
from app_settings import zmq_router_fe, zmq_router_be

def printer(stream, msg):
    print "ZMQ Received: %s" % msg

ctx = zmq.Context()
s_be = ctx.socket(zmq.ROUTER)
s_be.bind('tcp://*:%d' % zmq_router_be)
s_fe = ctx.socket(zmq.ROUTER)
s_fe.bind('tcp://*:%d' % zmq_router_fe)

workers = []
poller = zmq.Poller()
# Only poll for requests from backend until workers are available
poller.register(s_be, zmq.POLLIN)
while True:
    print("Polling for connections...")
    sockets = dict(poller.poll())
    if s_be in sockets:
        # Handle worker activity on the backend
        request = s_be.recv_multipart()
        worker, empty, client = request[:3]
        if not workers:
            poller.register(s_fe, zmq.POLLIN)
        workers.append(worker)
        if client != b"READY" and len(request) > 3:
            # If client reply, send rest back to frontend
            empty, reply = request[3:]
            s_fe.send_multipart([client, b"", reply])
        else:
            print worker + ", " + client

    if s_fe in sockets:
        # Get next client request, route to last-used worker
        request = s_fe.recv_multipart()
        client, empty, cmd = request[:3]
        worker = workers.pop(0)
        if len(request) > 3:
            s_be.send_multipart([worker, b"", client, b"", cmd, request[3] ])
        else:
            s_be.send_multipart([worker, b"", client, b"", cmd])
        if not workers:
            # Don't poll clients if no workers are available
            poller.unregister(s_fe)

s_fe.close()
s_be.close()
