import threading
import zmq

running = True
socket = None

def run():
	global socket

	print("connecting to zmq server")
	context = zmq.Context()
	socket = context.socket(zmq.REQ)
	socket.connect("tcp://localhost:5555")
	print("connected to zmq server")
	
	#t = threading.Thread(target=startReceivingThread)
	#t.setDaemon(True)
	#t.start();

	while running:
		msg = input()
		socket.send(msg.encode("utf-8"))
		msg = socket.recv()
		print(msg.decode("utf-8"))

def startReceivingThread():
	while running:
		msg = socket.recv()
		print(msg)

run()