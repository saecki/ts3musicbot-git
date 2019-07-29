import os
import multiprocessing
import time
import json
import re
import urllib.request
from bs4 import BeautifulSoup

#local imports
import ts3musicbot as bot
from common.classproperties import TS3MusicBotModule
from common.classproperties import Command
from common.classproperties import Argument
from common.classproperties import Playlist
from common.constants import Prefixes
from common.constants import Commands
from common.constants import Args
from common.constants import ArgValues

class CLI(TS3MusicBotModule):

	def __init__(self):
		super().__init__()
		self.lastLine = self.getLineCountOf(CLI.getTS3ChannelChatFilePath())
		self.report("waiting for a command")

	def update(self):
		self.checkForTeamspeakCommand()
		#self.checkForTerminalCommand()
	
	def report(self, string):
		print(string)
		self.sendToChannel(string)

	def checkForTeamspeakCommand(self):
		#try:
		currentLine = self.getLineCountOf(CLI.getTS3ChannelChatFilePath())
		if  currentLine > self.lastLine:
			with open(CLI.getTS3ChannelChatFilePath()) as f:
				for line in f:
					pass
				string = CLI.stripTS3Chat(line)
				command = CLI.stringToCommand(string)
				self.handleCommand(command, Prefixes.Teamspeak)
				self.lastLine = currentLine
		#except:
		#	self.report("couldn't retrieve new command")

	def checkForTerminalCommand(self):
		string = input()
		command = CLI.stringToCommand(string)
		self.handleCommand(command)

	#
	#commands
	#

	def handleCommand(self, command, prefix=""):
		if not command == None:
			if command.name.startswith(prefix):
				command.name = command.name[len(prefix):]
				if command.name == Commands.Play:
					self.play(command)
				elif command.name == Commands.PlayNext:
					self.playNext(command)
				elif command.name == Commands.PlayNow:
					self.playNow(command)
				elif command.name == Commands.PlayQueue:
					self.playQueue(command)
				elif command.name == Commands.Remove:
					self.remove(command)
				elif command.name == Commands.RemoveNext:
					self.removeNext()
				elif command.name == Commands.RemoveCurrent:
					self.removeCurrent()
				elif command.name == Commands.Pause:
					self.pause()
				elif command.name == Commands.Previous:
					self.previous()
				elif command.name == Commands.Next:
					self.next()
				elif command.name == Commands.Stop:
					self.stop()
				elif command.name == Commands.Clear:
					self.clear()
				elif command.name == Commands.Shuffle:
					self.shuffle()
				elif command.name == Commands.Repeat:
					self.repeat(command)
				elif command.name == Commands.List:
					self.list()
				elif command.name == Commands.Volume:
					self.volume(command)
				elif command.name == Commands.Playlist:
					self.playlist(command)
				else:
					self.report("the command: " + command.name + " wasn't found")
			else:
				self.report("prefix not found")
		else:
			self.report("wow that's impressive")

	def stripTS3Chat(string):
		string = re.sub("<.*?: ","", string)

		return string


	def stringToCommand(string):

		string = string.rstrip()

		fields = string.split(" ")

		if len(fields) > 0:
			commandName = fields[0]

			command = Command(commandName)

			lastArg = None
			value = False
			
			for i in range(1, len(fields)):
				
				if value:	
					lastArg.value = fields[i]
					command.args.append(lastArg)

					value = False
				else:
					lastArg = Argument(fields[i])
					
					if fields[i].endswith(":"):
						value = True
					else:
						command.args.append(lastArg)

			return command

		else:
			return None

	#
	#server query api
	#

	def startServerQuery(self):
		pass

	def sendToChannel(self, string):
		pass

		#
		#maths stuff
		#

	def getNumberBetween(number, min, max):
		if number < min:
			return min
		elif number > max:
			return max
		else:
			return number

	#
	#file system
	#

	def getTS3ChannelChatFilePath():
		p = os.getenv("APPDATA")
		p += os.path.sep
		p += "TS3Client\\chats"

		all_subdirs = CLI.getAllSubdirsOf(p)
		latest_subdir = max(all_subdirs, key=os.path.getmtime)

		path = latest_subdir
		path += os.path.sep
		path += "channel.txt"

		return path

	def getAllSubdirsOf(b="."):
		result = []
		for d in os.listdir(b):
			bd = os.path.join(b, d)
			if os.path.isdir(bd): result.append(bd)
		return result

	def getLineCountOf(self, path):
		try:
			return sum(1 for line in open(path))
		except:
			self.report("couldn't get line count of file " + path)
			return 0

	#
	#url
	#

	def isURL(self, string):
		if "[URL]" in string and "[/URL]" in string:
			return True
		else:
			return False

	def getURL(self, string):
		url = string
		url = url.replace("[URL]", "")
		url = url.replace("[/URL]", "")

		return url

	def isYoutubeURL(self, url):
		if "youtu.be" in url or "youtube.com" in url:
			return True
		else:
			self.report("no valid youtube link")
			return False

	def getYoutubeURLFromString(self, string):
		try:
			query = urllib.parse.quote(string)
			url = "https://www.youtube.com/results?search_query=" + query
			response = urllib.request.urlopen(url)
			html = response.read()
			soup = BeautifulSoup(html, 'html.parser')
			
			for vid in soup.findAll(attrs={'class':'yt-uix-tile-link'}):
				return 'https://www.youtube.com' + vid['href']
		except:
			self.report("couldn't get get youtube url")
		
		return None
	
	#
	#queue
	#

	def play(self, command):
		if len(command.args) > 0:
			url = self.getYoutubeURLFromPlayCommand(command)
			if not url == None:
				bot.play(url)
		else:
			bot.play()

	def playNext(self, command):
		if len(command.args) > 0:
			url = self.getYoutubeURLFromPlayCommand(command)
			if not url == None:
				bot.playNext(url)
		else:
			self.report("not enough Args")

	def playNow(self, command):
		if len(command.args) > 0:
			url = self.getYoutubeURLFromPlayCommand(command)
			if not url == None:
				bot.playNow(url)
		else:
			self.report("not enough Args")

	def getYoutubeURLFromPlayCommand(self, command):
		if self.isURL(command.args[0].name):
			url = self.getURL(command.args[0].name)
			if self.isYoutubeURL(url):
				return url
			else:
				self.report("specified value is no youtube url")
		else:
			string = ""
			for arg in command.args:
				string += arg.name + " "

			url = self.getYoutubeURLFromString(string)
			
			if not url == None:
				return url
			else:
				self.report("couldn't find any video")
		
		return None


	def playQueue(self, command):
		if len(command.args) > 0:
			integer = True

			try:
				index = int(command.args[0].name)
			except:
				integer = False
				self.report("enter a valid number as argument")

			if integer:
				bot.playQueue(index)

	def remove(self, command):
		if len(command.args) > 0:
			integer = True

			try:
				index = int(command.args[0].name)
			except:
				integer = False
				self.report("enter a valid number as argument")

			if integer:
				bot.remove(index)

	def removeNext(self):
		bot.removeNext()

	def removeCurrent(self):
		bot.removeCurrent()

	def pause(self):
		bot.pause()

	def previous(self):
		bot.previous()

	def next(self):
		bot.next()

	def stop(self):
		bot.stop()

	def clear(self):
		bot.clear()

	def shuffle(self):
		bot.shuffle()

	def list(self):
		index = 0

		self.report("queue:")
		for s in bot.songQueue:
			if index == bot.index:
				self.report("> (" + str(index) + ") " + s)
			else:
				self.report("  (" + str(index) + ") " + s)
			index += 1

	def repeat(self, command):
		if len(command.args) > 0:
			if command.args[0].name == ArgValues.All:
				bot.repeat(2)
			elif command.args[0].name == ArgValues.Stop:
				bot.repeat(0)
			else:
				self.report("argument " + command.args[0].name + " not found")
		else:
			bot.repeat(1)

	def volume(self, command):
		if len(command.args) > 0:
			if command.args[0].name.startswith("+"):
				string = command.args[0].name[1:]
				volume = self.getNumberFromString(string)
				
				if not volume == None:
					bot.plusVolume(volume)

			elif command.args[0].name.startswith("-"):
				string = command.args[0].name[1:]
				volume = self.getNumberFromString(string)
				
				if not volume == None:
					bot.minusVolume(volume)

			else:
				volume = self.getNumberFromString(command.args[0].name)
				if not volume == None:
					bot.setVolume(volume)

	def getNumberFromString(self, string):
		try:
			num = int(string)
		except:
			self.report("not a number")
			return None
		return num

	#
	#playlist
	#

	def playlist(self, command):
		if len(command.args) > 0:
			if command.args[0].name == Args.Create:
				self.playlistCreate(command.args)
			elif command.args[0].name == Args.Delete:
				self.playlistDelete(command.args)
			elif command.args[0].name == Args.Add:
				self.playlistAdd(command.args)
			elif command.args[0].name == Args.Remove:
				self.playlistRemove(command.args)
			elif command.args[0].name == Args.Play:
				self.playlistPlay(command.args)
			elif command.args[0].name == Args.Queue:
				self.playlistQueue(command.args)
			elif command.args[0].name == Args.Shuffle:
				self.playlistShuffle(command.args)
			elif command.args[0].name == Args.Clear:
				self.playlistClear(command.args)
			elif command.args[0].name == Args.List:
				self.playlistList(command.args)
			else:
				self.report("argument " + command.args[0].name + " not found")
		else:
			self.report("not enough Args")

	def playlistCreate(self, args):
		name = args[0].value
		if len(args) > 1:
			if args[1].name == Args.From:
				if args[1].value == ArgValues.Queue:
					bot.playlistCreateFromQueue(name)
				else:
					p = bot.getPlaylist(args[1].value)
					if not p == None:
						bot.createPlaylistFrom(name, p)
					else:
						self.report("couldn't find playlist")
			else:
				self.report("specified argument not correct")
		else:
			bot.playlistCreate(name)

	def playlistDelete(self, args):
		p = bot.getPlaylist(args[0].value)
		if not p == None:
			bot.playlistDelete(p)
		else:
			self.report("playlist not found")

	def playlistAdd(self, args):
		if len(args) > 1:
			if args[1].name == Args.To:			
				p = bot.getPlaylist(args[1].value)
				if not p == None:					
					if self.isURL(args[0].value):
						url = self.getURL(args[0].value)
						if self.isYoutubeURL(url):
							bot.playlistAdd(url, p)
						else:
							self.report("specified value is no youtube url")
					else:
						self.report("specified value is no url")
				else:
					self.report("playlist not found")
			else:
				self.report("specified argument not correct")
		else:
			self.report("not enough Args")

	def playlistRemove(self, args):
		if len(args) > 1:
			if args[1].name == Args.From:
				p = bot.getPlaylist(args[1].value)
				if not p == None:
					integer = True

					try:
						index = int(args[0].value)
					except:
						integer = False
						self.report("enter a valid number as argument")

					if integer:
						bot.playlistRemove(index, p)
				else:
					self.report("playlist not found")
			else:
				self.report("specified argument not correct")
		else:
			self.report("not enough Args")

	def getYoutubeURLFromPlaylistCommand(self, command):
		if isURL(command.args[0].value):
			url = self.getURL(command.args[0].value)
			if isYoutubeURL(url):
				return url
			else:
				self.report("specified value is no youtube url")
		else:
			string = command.args[0].value + " "
			newArgs = command.args[1:]

			for arg in newArgs:
				string += arg.name + " "

			url = self.getYoutubeURLFromString(string)
			
			if not url == None:
				return url
			else:
				self.report("couldn't find any video")
		
		return None

	def playlistPlay(self, args):
		p = bot.getPlaylist(args[0].value)
		if not p == None:
			bot.playlistPlay(p)
		else:
			self.report("playlist not found")

	def playlistQueue(self, args):
		p = bot.getPlaylist(args[0].value)
		if not p == None:
			bot.playlistQueue(p)
		else:
			self.report("playlist not found")

	def playlistShuffle(self, args):
		p = bot.getPlaylist(args[0].value)
		if not p == None:
			bot.playlistShuffle(p)
		else:
			self.report("playlist not found")

	def playlistClear(self, args):
		p = bot.getPlaylist(args[0].value)
		if not p == None:
			bot.playlistClear(p)
		else:
			self.report("playlist not found")

	def playlistList(self, args):
		if args[0].value == ArgValues.All:
			self.playlistListAll()
		else:
			p = bot.getPlaylist(args[0].value)
			if not p == None:
				self.playlistListPlaylist(p)
			else:
				self.report("playlist not found")

	def playlistListAll(self):
		self.report("playlists:")
		for p in bot.playlists:
			self.report("")
			self.playlistListPlaylist(p)

	def playlistListPlaylist(self, playlist):
		index = 0
		self.report(playlist.name)
		for s in playlist.songURLs:
			self.report("(" + str(index) + ")   " + s)
			index += 1