import json
import time
import ts3

import ts3musicbot as bot

from common.classproperties import FileSystem
from common.constants import JSONFields
from common.constants import Prefixes
from modules import cli

clientQuery = None
disconnected = False

def run():
	global clientQuery

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

		self.APIKEY = ""
		self.NICKNAME = ""
		self.HOST = "localhost"

		self.readData()
		self.sendingConnection = self.createConnection(self.HOST, self.APIKEY)
		self.receivingConnection = self.createConnection(self.HOST, self.APIKEY)

		if self.sendingConnection == None or self.receivingConnection == None:
			disconnected = True
			print("most likely the teamspeak client isn't running or the clientquery apikey is wrong")
			print("running without teamspeak interface")
		else:
			self.updateBot()

	def readData(self):

		try:
			with open(FileSystem.getClientQueryFilePath()) as jsonfile:  
				data = json.load(jsonfile)	
				
				try:
					self.APIKEY = data[JSONFields.ApiKey]
				except:
					print("couldn't read apikey")

				try:
					self.NICKNAME = data[JSONFields.Nickname]
				except:
					print("couldn't read nickname")
			
			return True
		except:
			print("couldn't read config file")
			print("trying to create a ts3clientquery config file")
			try:
				with open(FileSystem.getClientQueryFilePath(), "w") as jsonfile:
					data = {}
					data[JSONFields.ApiKey] = "YOURAPIKEY"
					data[JSONFields.Nickname] = "Musicbot"

					json.dump(data, jsonfile, indent=4)

					print("created a config.json file in ts3musicbot/data you'll have to enter a ts3clientquery api key which can be found in your teamspeak client at: tools - options - addons - clientquery - settings. ")
			except FileExistsError:	
				print("couldn't create config file")
		return False

	def createConnection(self, HOST, APIKEY):
		try:
			ts3conn = ts3.query.TS3ClientConnection(HOST)
			ts3conn.auth(apikey=APIKEY)
			ts3conn.use()
			return ts3conn
		except:
			print("couldn't connect to teamspeak")
		return None

	def updateBot(self):
		try:
			clientinfo = self.sendingConnection.whoami()
			clientid = clientinfo[0]["clid"]
			clientvariables = self.sendingConnection.clientvariable(clientid, "client_nickname")
			clientnickname = clientvariables[0]["client_nickname"]

			if self.NICKNAME != clientnickname:
				self.setNickname(self.NICKNAME)
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

	def getDatabaseClientID(self):
		try:
			clid = self.getClientID(self.sendingConnection)
			clients = self.sendingConnection.clientlist()

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
			channelID = self.getCurrentChannelID(self.sendingConnection)
		except:
			print("couldn't get channel id")

		time.sleep(0.01)

		if channelID != None:
			try:
				self.sendingConnection.sendtextmessage(targetmode=2, target=channelID, msg=message)
			except:
				print("couldn't send to channel")

		time.sleep(0.1)

	def setNickname(self, nickname):
		try:
			self.sendingConnection.clientupdate(client_nickname=nickname)
		except:
			print("couldn't update nickname")


	def setDescription(self, description):
		cldbid = self.getDatabaseClientID()

		if cldbid != None:
			self.sendingConnection.clientdbedit(cldbid=cldbid, client_description=description)
		else:
			print("couldn't update description")

	def registerForTextEvents(self):
		try:
			self.receivingConnection.clientnotifyregister(event="notifytextmessage", schandlerid=1)
		except:
			print("couldn't register for text events from the teamspeak client")

	def listenForTextEvents(self, timeout=60):

		try:
			event = self.receivingConnection.wait_for_event(timeout=timeout)
			clid = self.getClientID(self.receivingConnection)
			if event[0]["invokerid"] != clid:
				print(event[0]["msg"])
				return event[0]["msg"]
		except:
			pass
		
		return None

	def sendKeepalive(self):
		try:
			self.receivingConnection.send_keepalive()
		except:
			print("couldn't send keep alive to the teamspeak client")