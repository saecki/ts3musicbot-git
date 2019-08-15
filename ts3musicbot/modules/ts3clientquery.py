import ts3
import json
import time

from common.classproperties import FileSystem

class ClientQuery:

	def __init__(self):
		self.APIKEY = ""
		self.NICKNAME = ""
		self.HOST = "localhost"
		self.lastLine = FileSystem.getLineCountOf(FileSystem.getTS3ChannelChatFilePath())

		self.readData()
		self.sendingConnection = self.connectAndAuthenticate(self.HOST, self.APIKEY)
		self.receivingConnection = self.connectAndAuthenticate(self.HOST, self.APIKEY)
		self.updateBot()

	def readData(self):

		try:
			with open(FileSystem.getClientQueryFilePath()) as jsonfile:  
				data = json.load(jsonfile)	
				
				try:
					self.APIKEY = data["APIKEY"]
				except:
					print("couldn't read apikey")

				try:
					self.NICKNAME = data["NICKNAME"]
				except:
					print("couldn't read nickname")
			
			return True
		except:
			print("couldn't read config file")
			print("trying to create a ts3clientquery config file")
			try:
				with open(FileSystem.getClientQueryFilePath(), "w") as jsonfile:
					data = {}
					data["APIKEY"] = "YOURAPIKEY"
					data["NICKNAME"] = "BOTNICKNAME"

					json.dump(data, jsonfile)

					print("created ts3clientquery.json file in APPDATA/roaming/TS3MusicBot/ you'll have to enter the name of the bot the your ts3clientquery apikey")
			except FileExistsError:	
				print("couldn't create ts3clientquery config file")
		return False

	def connectAndAuthenticate(self, HOST, APIKEY):
		try:
			ts3conn = ts3.query.TS3ClientConnection(HOST)
			ts3conn.auth(apikey=APIKEY)
			ts3conn.use()
			return ts3conn
		except:
			print("couldn't connect to teamspeak")
		return None

	def updateBot(self):
		clientinfo = self.sendingConnection.whoami()
		clientid = clientinfo[0]["clid"]
		clientvariables = self.sendingConnection.clientvariable(clientid, "client_nickname")
		clientnickname = clientvariables[0]["client_nickname"]

		if not self.NICKNAME == clientnickname:
			try:
				self.sendingConnection.clientupdate(client_nickname=self.NICKNAME)
			except:
				print("couldn't update nickname")

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
			clients = self.sendingConnection.clientlist()

			for c in clients:
				if c["client_nickname"] == self.NICKNAME:
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

		if not channelID == None:
			try:
				self.sendingConnection.sendtextmessage(targetmode=2, target=channelID, msg=message)
			except:
				print("couldn't send to channel")

		time.sleep(0.1)

	def setDescription(self, description):
		cldbid = self.getDatabaseClientID()

		if not cldbid == None:
			self.sendingConnection.clientdbedit(cldbid=cldbid, client_description=description)
		else:
			print("couldn't update description")

	def registerForTextEvents(self):
		self.receivingConnection.clientnotifyregister(event="notifytextmessage", schandlerid=1)

	def listenForTextEvents(self, timeout=60):

		try:
			event = self.receivingConnection.wait_for_event(timeout=timeout)
			if not event[0]["invokername"] == self.NICKNAME:
				print(event[0]["msg"])
				return event[0]["msg"]
		except:
			pass
		
		return None

	def sendKeepalive(self):
		self.receivingConnection.send_keepalive()