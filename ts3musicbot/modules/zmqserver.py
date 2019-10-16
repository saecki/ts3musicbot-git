import zmq

import ts3musicbot as bot
from modules import cli

publisher = None
collector = None

def run():
	global publisher
	global collector
	
	print("starting zmq server")
	context = zmq.Context()
	publisher = context.socket(zmq.PUB)
	publisher.bind("tcp://127.0.0.1:5557")
	collector = context.socket(zmq.PULL)
	collector.bind("tcp://127.0.0.1:5558")

	bot.addThread(target=startCollector, daemon=True)
	print("started zmq server")

def update():
	pass

def report(string):
	msg = string.encode("utf-8")
	publisher.send(msg)

def startCollector():
	while bot.running:
	    msg = collector.recv()
	    string = msg.decode("utf-8")

	    if bot.debug:
	    	print("received zmq message msg: " + string)

	    with bot.lock:
	    	cli.handleCommand(cli.parseCommand(string))