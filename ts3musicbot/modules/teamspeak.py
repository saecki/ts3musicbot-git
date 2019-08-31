import json
import time
import ts3

import ts3musicbot as bot

from common.classproperties import FileSystem
from common.constants import Commands
from common.constants import JSONFields
from common.constants import Prefixes
from modules import cli

APIKEY = ""
NICKNAME = ""
SERVERADDRESS = ""
HOST = "localhost"

clientQuery = None
disconnected = False

def run():
	global clientQuery

	readData()
	clientQuery = ClientQuery(HOST, APIKEY)
	nicknameIndex = 0

	if not disconnected:
		clientQuery.connect(SERVERADDRESS)
		updateBot()

		bot.addThread(target=startKeepingAliveQueryConnection, daemon=True)
		bot.addThread(target=startCheckingForTeamspeakCommand, daemon=True)

def update():
	if not disconnected:
		updateDescription()

def report(string):
	if not disconnected:
		sendToChannel(string)

def readData():
	global APIKEY
	global NICKNAME
	global SERVERADDRESS

	try:
		with open(FileSystem.getClientQueryFilePath()) as jsonfile:  
			data = json.load(jsonfile)	
			
			try:
				APIKEY = data[JSONFields.ApiKey]
			except:
				print("couldn't read apikey")

			try:
				NICKNAME = data[JSONFields.Nickname]
			except:
				print("couldn't read nickname")

			try:
				SERVERADDRESS = data[JSONFields.ServerAddress]
			except Exception as e:
				print("couldn't read SERVERADDRESS")
				print(e)

		return True
	except:
		print("couldn't read config file")
		print("trying to create a ts3clientquery config file")
		try:
			with open(FileSystem.getClientQueryFilePath(), "w") as jsonfile:
				data = {}	
				data[JSONFields.ApiKey] = "YOURAPIKEY"
				data[JSONFields.Nickname] = "Musicbot"
				data[JSONFields.ServerAddress] = ""

				json.dump(data, jsonfile, indent=4)

				print("created a config.json file in ts3musicbot/data you'll have to enter a ts3clientquery api key which can be found in your teamspeak client at: tools - options - addons - clientquery - settings. ")
		except FileExistsError:	
			print("couldn't create config file")
	return False

def startKeepingAliveQueryConnection():
	while bot.running:
		with bot.clientQueryLock:
			clientQuery.sendKeepalive()
		time.sleep(200)

def startCheckingForTeamspeakCommand():
	clientQuery.registerForTextEvents()

	while bot.running:
		string = clientQuery.listenForTextEvents()
		if string != None:
			command = cli.stringToCommand(string)
			with bot.lock:
				cli.handleCommand(command, prefix=Prefixes.Teamspeak)

def handleTeamspeakCommand(event):
	try:
		msg = event["msg"]
		if msg in Commands.ComeOver:
			comeOver(event)
		else:
			return False
		return True
	except:
		return False

def updateBot():
	try:
		clientQuery.setNickname(NICKNAME)
	except:
		print("couldn't update nickname")

def updateDescription():
	msg = cli.getPlaybackInfo()
	
	with bot.clientQueryLock:
		clientQuery.setDescription(msg)

def sendToChannel(string):
	with bot.clientQueryLock:
		clientQuery.sendMessageToCurrentChannel(string)

def comeOver(event):
	try:
		clientID = event["invokerid"]
		channelID = clientQuery.getChannelID(clientID)
		self.moveToChannel(channelID)
	except Exception as e:
		print("couldn't move over")
		print(e)

class ClientQuery:

	def __init__(self, HOST, APIKEY):
		global disconnected

		self.mainConnection = self.createQuery(HOST, APIKEY)
		self.listeningConnection = self.createQuery(HOST, APIKEY)

		if self.mainConnection == None or self.listeningConnection == None:
			disconnected = True
			print("most likely the teamspeak client isn't running or the clientquery apikey is wrong")
			print("running without teamspeak interface")

	def createQuery(self, HOST, APIKEY):
		try:
			ts3conn = ts3.query.TS3ClientConnection(HOST)
			ts3conn.auth(apikey=APIKEY)
			ts3conn.use()
			return ts3conn
		except Exception as e:
			print("couldn't connect to teamspeak")
			print(e)
		return None

	def connect(self, address):
		if len(address) > 0:
			try:
				serverInfo = None
				try:
					serverInfo = self.mainConnection.serverconnectinfo()
				except:
					return self.mainConnection.send("connect", {"address":address})
			except Exception as e:
				print("couldn't connect to " + address)
				print(e)

	def moveToChannel(channelID):
		try:
			clientID = getClientID()
			mainConnection.clientmove(cid=channelID, clid=clientID)
		except Exception as e:
			print("couldn't move to channel with id " + channelID)
			print(e)

	def sendMessageToCurrentChannel(self, message):
		try:
			channelID = self.getCurrentChannelID()
		except Exception as e:
			print("couldn't get channel id")

		if channelID != None:
			try:
				self.mainConnection.sendtextmessage(targetmode=2, target=channelID, msg=message)
			except Exception as e:
				print("couldn't send message to channel")
				print(e)

	def registerForTextEvents(self):
		try:
			self.listeningConnection.clientnotifyregister(event="notifytextmessage", schandlerid=1)
		except Exception as e:
			print("couldn't register for text events from the teamspeak client")
			print(e)

	def listenForTextEvents(self, timeout=60):
		try:
			event = self.listeningConnection.wait_for_event(timeout=timeout)
			clientID = self.getClientID()
			invokerID = event[0]["invokerid"]
			msg = event[0]["msg"]
			if invokerID != clientID or bot.debug:
				print("invokerid: " + invokerid + " msg: " + msg)
				if not handleTeamspeakCommand(event):
					return msg
		except:
			pass
		
		return None

	def sendKeepalive(self):
		try:
			self.listeningConnection.send_keepalive()
		except Exception as e:
			print("couldn't send keep alive to the teamspeak client")
			print(e)

	def setNickname(self, nickname):
		try:
			clientID = self.getClientID()
			clientVariables = self.mainConnection.clientvariable(clientID, "client_nickname")
			clientnickname = clientVariables[0]["client_nickname"]
			if nickname != clientnickname:
				self.mainConnection.clientupdate(client_nickname=nickname)
		except Exception as e:
			print("couldn't update teamspeak nickname")
			print(e)

	def setDescription(self, description):
		try:
			clientDatabaseID = self.getDatabaseClientID()
			self.mainConnection.clientdbedit(cldbid=clientDatabaseID, client_description=description)
		except Exception as e:
			print("couldn't update teamspeak description")
			print(e)

	def getClientID(self):
		try:
			clientInfo = self.mainConnection.whoami()
			clientID = clientInfo[0]["clid"]
			return clientID
		except Exception as e:
			print("couldn't get client id")
			print(e)

		return None

	def getCurrentChannelID(self):
		try:
			clientInfo = self.mainConnection.whoami()
			channelID = clientInfo[0]["cid"]
			return channelID
		except Exception as e:
			print("couldn't get channel id")
			print(e)

		return None

	def getChannelID(self, clientID):
		try:
			clientVariables = self.mainConnection.clientvariable(clientID, "cid")
			channelID = clientVariables["cid"]
			return channelID
		except Exception as e:
			print("couldn't get channel id")
			print(e)
		
		return None

	def getDatabaseClientID(self):
		try:
			clientID = self.getClientID()
			clientVariables = self.mainConnection.clientvariable(clientID, "client_database_id")
			clientDatabaseID = clientVariables["client_database_id"]
			return clientDatabaseID
		except Exception as e:
			print("couldn't get client database id")
			print(e)

		return None