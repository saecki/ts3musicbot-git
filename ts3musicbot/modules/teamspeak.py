import json
import time
import ts3

import ts3musicbot as bot

from common.classproperties import FileSystem
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
	clientQuery = ClientQuery()
	nicknameIndex = 0

	if not disconnected:
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

def sendToChannel(string):
	with bot.clientQueryLock:
		clientQuery.sendMessageToCurrentChannel(string)

def updateNickname():
	msg = cli.getCurrentSongTitle()

	if msg != None:
		if nicknameIndex > len(msg) - 5:
			nicknameIndex = 0
		
		msg = msg[nicknameIndex:]

		nickname = msg[:30] if len(msg) > 30 else msg

		nicknameIndex += 1
	
	else:
		nickname = clientQuery.NICKNAME

	with bot.clientQueryLock:
		clientQuery.setNickname(nickname)


def updateDescription():
	msg = cli.getPlaybackInfo()
	
	with bot.clientQueryLock:
		clientQuery.setDescription(msg)

class ClientQuery:

	def __init__(self):
		global disconnected

		self.mainConnection = self.createQuery(HOST, APIKEY)
		self.listeningConnection = self.createQuery(HOST, APIKEY)

		if self.mainConnection == None or self.listeningConnection == None:
			disconnected = True
			print("most likely the teamspeak client isn't running or the clientquery apikey is wrong")
			print("running without teamspeak interface")
		else:
			self.updateBot()
			#self.connect()

	def createQuery(self, HOST, APIKEY):
		try:
			ts3conn = ts3.query.TS3ClientConnection(HOST)
			ts3conn.auth(apikey=APIKEY)
			ts3conn.use()	
			return ts3conn
		except:
			print("couldn't connect to teamspeak")
		return None

	def connect(self):
		if len(SERVERADDRESS) > 0:
			try:
				serverInfo = self.mainConnection.serverconnectinfo()
				if serverInfo["ip"] != SERVERADDRESS:
					self.mainConnection.connect(address=SERVERADDRESS) #TODO replace with correct function
			except:
				print("couldn't connect to " + SERVERADDRESS)

	def updateBot(self):
		try:
			clientinfo = self.mainConnection.whoami()
			clientid = clientinfo[0]["clid"]
			clientvariables = self.mainConnection.clientvariable(clientid, "client_nickname")
			clientnickname = clientvariables[0]["client_nickname"]

			if NICKNAME != clientnickname:
				self.setNickname(NICKNAME)
		except:
			print("couldn't update nickname")

	def getClientID(self, ts3conn):
		try:
			clientinfo = ts3conn.whoami()
			channelID = clientinfo[0]["clid"]
			return channelID
		except:
			print("couldn't get client id")

		return None

	def getCurrentChannelID(self, ts3conn):
		try:
			clientinfo = ts3conn.whoami()
			channelID = clientinfo[0]["cid"]
			return channelID
		except:
			print("couldn't get channel id")

		return None

	def connectToChannel(cid):
		clid = getClientID()
		if clid != None:
			mainConnection.clientmove(cid=cid, clid=clid)

	def getDatabaseClientID(self):
		try:
			clid = self.getClientID(self.mainConnection)
			clients = self.mainConnection.clientlist()

			for c in clients:
				if c["clid"] == clid:
					cldbid = c["client_database_id"]
					return cldbid
		except:
			print("couldn't get client database id")

		return None

	def sendMessageToCurrentChannel(self, message):
		time.sleep(0.01)

		try:
			channelID = self.getCurrentChannelID(self.mainConnection)
		except:
			print("couldn't get channel id")

		time.sleep(0.01)

		if channelID != None:
			try:
				self.mainConnection.sendtextmessage(targetmode=2, target=channelID, msg=message)
			except:
				print("couldn't send to channel")

		time.sleep(0.1)

	def setNickname(self, nickname):
		try:
			self.mainConnection.clientupdate(client_nickname=nickname)
		except:
			print("couldn't update nickname")


	def setDescription(self, description):
		cldbid = self.getDatabaseClientID()

		if cldbid != None:
			self.mainConnection.clientdbedit(cldbid=cldbid, client_description=description)
		else:
			print("couldn't update description")

	def registerForTextEvents(self):
		try:
			self.listeningConnection.clientnotifyregister(event="notifytextmessage", schandlerid=1)
		except:
			print("couldn't register for text events from the teamspeak client")

	def listenForTextEvents(self, timeout=60):

		try:
			event = self.listeningConnection.wait_for_event(timeout=timeout)
			clid = self.getClientID(self.listeningConnection)
			if event[0]["invokerid"] != clid:
				print(event[0]["msg"])
				return event[0]["msg"]
		except:
			pass
		
		return None

	def sendKeepalive(self):
		try:
			self.listeningConnection.send_keepalive()
		except:
			print("couldn't send keep alive to the teamspeak client")