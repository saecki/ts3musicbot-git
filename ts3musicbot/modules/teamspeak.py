import json
import subprocess
import telnetlib
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
TEAMSPEAKPATH = ""

clientQuery = None
disconnected = False

lastDescription = None

def run():
	global clientQuery
	global disconnected

	readData()
	startTeamspeakThread(TEAMSPEAKPATH)
	clientQuery = ClientQuery(HOST, APIKEY)
	nicknameIndex = 0

	if not disconnected:
		if len(SERVERADDRESS) > 0:
			if clientQuery.tryConnecting(SERVERADDRESS):
				updateBot()
				bot.addThread(target=startCheckingForTeamspeakCommand, daemon=True)
		elif clientQuery.isConnected():
			updateBot()
			bot.addThread(target=startCheckingForTeamspeakCommand, daemon=True)
		else:
			disconnected = True
			print("connect to a teamspeak server first or set a server address in the config.json file")
			print("running without teamspeak interface")

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
	global TEAMSPEAKPATH

	try:
		with open(FileSystem.getConfigFilePath()) as jsonfile:  
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
				print("couldn't read serveradress")

			try:
				TEAMSPEAKPATH = data[JSONFields.TeamspeakPath]
			except Exception as e:
				print("couldn't read teamspeakpath")

		return True
	except:
		print("couldn't read config file")
		print("trying to create a ts3clientquery config file")
		try:
			with open(FileSystem.getConfigFilePath(), "w") as jsonfile:
				data = {}	
				data[JSONFields.ApiKey] = "YOURAPIKEY"
				data[JSONFields.Nickname] = "Musicbot"
				data[JSONFields.ServerAddress] = ""
				data[JSONFields.TeamspeakPath] = ""

				json.dump(data, jsonfile, indent=4)

				print("created a config.json file in " + FileSystem.getDataFolderPath() + "you'll have to enter a ts3clientquery api key which can be found in your teamspeak client at: tools - options - addons - clientquery - settings. ")
		except FileExistsError:	
			print("couldn't create config file")
	return False

def startTeamspeakThread(teamspeakPath):
	if len(teamspeakPath) > 0:
		print("starting teamspeak in: " + teamspeakPath)
		bot.startNewThread(target=startTeamspeak, args=(teamspeakPath,))
		for i in range(100):
			time.sleep(0.2)
			try:
				tn = telnetlib.Telnet(HOST, 25639)
			except:
				print("starting...")
			else:
				tn.close()
				del tn
				print("started teamspeak")
				return True
		print("starting teamspeak failed")
		return False


def startTeamspeak(teamspeakPath):
	subprocess.call(teamspeakPath)

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
		msg = event[0]["msg"]
		startswithprefix = None
		for p in Prefixes.Teamspeak:
			if msg.startswith(p):
				startswithprefix = p
				break

		if startswithprefix != None:
			command = msg[len(startswithprefix):]
			if command in Commands.ComeOver:
				comeOver(event)
			else:
				return False
			return True
	except Exception as e:
		print(e)
		return False

def updateBot():
	try:
		with bot.clientQueryLock:
			clientQuery.setNickname(NICKNAME)
	except:
		print("couldn't update nickname")

def updateDescription():
	global lastDescription

	msg = cli.getPlaybackInfo()

	if not msg == lastDescription:
		
		with bot.clientQueryLock:
			clientQuery.setDescription(msg)
		lastDescription = msg

def sendToChannel(string):
	with bot.clientQueryLock:
		clientQuery.sendMessageToCurrentChannel(string)

def comeOver(event):
	try:
		clientID = event[0]["invokerid"]
		channelID = clientQuery.getChannelID(clientID)
		clientQuery.moveToChannel(channelID)
	except Exception as e:
		print("couldn't come over")
		print(e)

class ClientQuery:

	def __init__(self, HOST, apikey):
		global disconnected

		self.host = HOST

		self.mainConnection = self.createQuery(HOST, apikey)
		self.listeningConnection = self.createQuery(HOST, apikey)

		if self.mainConnection == None or self.listeningConnection == None:
			disconnected = True
			print("most likely the teamspeak client isn't running or the clientquery apikey is wrong")
			print("running without teamspeak interface")

	def createQuery(self, HOST, apikey):
		try:
			ts3conn = ts3.query.TS3ClientConnection(HOST)
			ts3conn.auth(apikey=apikey)
			ts3conn.use()
			return ts3conn
		except Exception as e:
			print("couldn't connect to teamspeak")
			print(e)
		return None

	#
	#connection
	#

	def tryConnecting(self, address):
		print("connecting to " + address)
		self.connect(address)
		for i in range(50):
			time.sleep(0.2)
			if self.isConnected():
				print("connected to " + address)
				time.sleep(0.5)
				return True
			else:
				print("connecting...")
		print("connection failed")
		return False

	def connect(self, address):
		if len(address) > 0:
			try:
				serverInfo = None
				try:
					serverInfo = self.mainConnection.serverconnectinfo()
				except:
					self.mainConnection.send("connect", {"address":address})
				else:
					if serverInfo[0]["ip"] != address:
						self.mainConnection.send("connect", {"address":address})
			except Exception as e:
				print("couldn't connect to " + address)
				raise e

	def isConnected(self):
		try:
			serverInfo = self.mainConnection.serverconnectinfo()
			return True
		except Exception as e:
			return False

	def moveToChannel(self, channelID):
		try:
			clientID = self.getClientID()
			self.mainConnection.clientmove(cid=channelID, clid=clientID)
		except Exception as e:
			print("couldn't move to channel with id " + channelID)
			raise e

	def sendMessageToCurrentChannel(self, message):
		try:
			channelID = self.getCurrentChannelID()
			self.mainConnection.sendtextmessage(targetmode=2, target=channelID, msg=message)
		except Exception as e:
			print("couldn't get channel id")
			raise e

	def setNickname(self, nickname):
		try:
			clientID = self.getClientID()
			clientVariables = self.mainConnection.clientvariable(clientID, "client_nickname")
			clientnickname = clientVariables[0]["client_nickname"]
			if nickname != clientnickname:
				self.mainConnection.clientupdate(client_nickname=nickname)
		except Exception as e:
			print("couldn't update teamspeak nickname")
			raise e

	def setDescription(self, description):
		try:
			clientDatabaseID = self.getDatabaseClientID()
			self.mainConnection.clientdbedit(cldbid=clientDatabaseID, client_description=description)
		except Exception as e:
			print("couldn't update teamspeak description")
			raise e

	def getClientID(self):
		try:
			clientInfo = self.mainConnection.whoami()
			clientID = clientInfo[0]["clid"]
			return clientID
		except Exception as e:
			print("couldn't get client id")
			raise e

		return None

	def getCurrentChannelID(self):
		try:
			clientInfo = self.mainConnection.whoami()
			channelID = clientInfo[0]["cid"]
			return channelID
		except Exception as e:
			print("couldn't get current channel id")
			raise e

		return None

	def getChannelID(self, clientID):
		try:
			clients = self.mainConnection.clientlist()
			for c in clients:
				if c["clid"] == clientID:
					return c["cid"]
		except Exception as e:
			print("couldn't get channel id")
			raise e
		
		return None

	def getDatabaseClientID(self):
		try:
			clientID = self.getClientID()

			clientVariables = self.mainConnection.clientvariable(clientID, "client_database_id")
			clientDatabaseID = clientVariables[0]["client_database_id"]

			return clientDatabaseID
		except Exception as e:
			print("couldn't get client database id")
			raise e

		return None

	#
	#eventlistening
	#

	def registerForTextEvents(self):
		try:
			self.listeningConnection.clientnotifyregister(event="notifytextmessage", schandlerid=1)
		except Exception as e:
			print("couldn't register for text events from the teamspeak client")
			raise e

	def listenForTextEvents(self, timeout=200):
		try:
			event = self.listeningConnection.wait_for_event(timeout=timeout)
		except:
			pass
		else:
			clientInfo = self.listeningConnection.whoami()
			clientID = clientInfo[0]["clid"]
			invokerID = event[0]["invokerid"]
			msg = event[0]["msg"]
			if bot.debug:
				print("invokerid: " + invokerID + " msg: " + msg)
				if not handleTeamspeakCommand(event):
					return msg
			elif invokerID != clientID:
				if not handleTeamspeakCommand(event):
					return msg
			self.listeningConnection.send_keepalive()