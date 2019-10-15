import zmq

import ts3musicbot as bot
from modules import cli

socket = None

def run():
	global socket

	print("starting zmq server")
	context = zmq.Context()
	socket = context.socket(zmq.REP)
	socket.bind("tcp://*:5555")
	bot.addThread(target=startZMQServer, daemon=True)
	print("started zmq server")

def update():
	pass

def report(string):
	#socket.send(string)
	pass

def startZMQServer():
	while True:
	    msg = socket.recv()
	    string = msg.decode("utf-8")

	    if bot.debug:
	    	print("received zmq message msg: " + string)

	    with bot.lock:
	    	cli.handleCommand(cli.parseCommand(string))
	    socket.send(b"...")