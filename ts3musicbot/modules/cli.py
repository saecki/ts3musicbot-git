import json
import multiprocessing
import os
import re
import time
import ts3
import urllib.request

from bs4 import BeautifulSoup

import ts3musicbot as bot

from common.classproperties import Argument
from common.classproperties import Command
from common.classproperties import Playlist
from common.classproperties import Song
from common.classproperties import TS3MusicBotModule

from common.constants import ArgValues
from common.constants import Args
from common.constants import Commands
from common.constants import Prefixes

from .ts3clientquery import ClientQuery

class CLI(TS3MusicBotModule):

	def __init__(self):
		super().__init__()

		if not bot.terminalOnly:
			self.clientQuery = ClientQuery()
			self.nicknameIndex = 0

		if not bot.terminalOnly:
			bot.addThread(target=self.startKeepingAliveQueryConnection, daemon=True)
			bot.addThread(target=self.startCheckingForTeamspeakCommand, daemon=True)
		
		bot.addThread(target=self.startCheckingForTerminalCommand, daemon=True)

		self.report("waiting for a command")

	def update(self):
		self.updateDescription()
		#self.updateNickname()
	
	def report(self, string):
		print(string)
		self.sendToChannel(string)

	#
	#ts3clientquery
	#

	def startKeepingAliveQueryConnection(self):
		while bot.running:
			with bot.clientQueryLock:
				self.clientQuery.sendKeepalive()
			time.sleep(200)

	def startCheckingForTeamspeakCommand(self):
		self.clientQuery.registerForTextEvents()

		while bot.running:
			string = self.clientQuery.listenForTextEvents()
			if not string == None:
				command = CLI.stringToCommand(string)
				with bot.lock:
					self.handleCommand(command, prefix=Prefixes.Teamspeak)

	def sendToChannel(self, string):
		if not bot.terminalOnly:
			with bot.clientQueryLock:
				self.clientQuery.sendMessageToCurrentChannel(string)

	def updateNickname(self):
		if not bot.terminalOnly:
			msg = bot.getCurrentSongTitle()

			if not msg == None:
				if self.nicknameIndex > len(msg) - 5:
					self.nicknameIndex = 0
				
				msg = msg[self.nicknameIndex:]

				nickname = msg[:30] if len(msg) > 30 else msg

				self.nicknameIndex += 1
			
			else:
				nickname = self.clientQuery.NICKNAME

			with bot.clientQueryLock:
				self.clientQuery.setNickname(nickname)


	def updateDescription(self):
		if not bot.terminalOnly:
			msg = bot.getPlaybackInfo()
			
			with bot.clientQueryLock:
				self.clientQuery.setDescription(msg)

	#
	#terminal
	#

	def startCheckingForTerminalCommand(self):
		while bot.running:
			try:
				string = input()
			except:
				print("terminal input failed")
			else:
				if string == "exit":
					bot.quit()
				command = CLI.stringToCommand(string)
				with bot.lock:
					self.handleCommand(command)

	#
	#commands
	#

	def handleCommand(self, command, prefix=""):
		if not command == None:
			if command.name.startswith(prefix):
				command.name = command.name[len(prefix):]
				if command.name in Commands.Commands[Commands.Play]:
					self.play(command)
				elif command.name in Commands.Commands[Commands.PlayNext]:
					self.playNext(command)
				elif command.name in Commands.Commands[Commands.PlayNow]:
					self.playNow(command)
				elif command.name in Commands.Commands[Commands.PlayQueue]:
					self.playQueue(command)
				elif command.name in Commands.Commands[Commands.Remove]:
					self.remove(command)
				elif command.name in Commands.Commands[Commands.RemoveNext]:
					self.removeNext()
				elif command.name in Commands.Commands[Commands.RemoveCurrent]:
					self.removeCurrent()
				elif command.name in Commands.Commands[Commands.Pause]:
					self.pause()
				elif command.name in Commands.Commands[Commands.Previous]:
					self.previous()
				elif command.name in Commands.Commands[Commands.Next]:
					self.next()
				elif command.name in Commands.Commands[Commands.Stop]:
					self.stop()
				elif command.name in Commands.Commands[Commands.Clear]:
					self.clear()
				elif command.name in Commands.Commands[Commands.Shuffle]:
					self.shuffle()
				elif command.name in Commands.Commands[Commands.Repeat]:
					self.repeat(command)
				elif command.name in Commands.Commands[Commands.List]:
					self.list()
				elif command.name in Commands.Commands[Commands.Position]:
					self.position(command)				
				elif command.name in Commands.Commands[Commands.Speed]:
					self.speed(command)
				elif command.name in Commands.Commands[Commands.Volume]:
					self.volume(command)
				elif command.name in Commands.Commands[Commands.Playlist]:
					self.playlist(command)
				else:
					self.report("the command: " + command.name + " wasn't found")
			else:
				self.report("prefix not found")
		else:
			self.report("wow that's impressive")

	def stringToCommand(string):

		if type(string) == str:
			string = string.rstrip()
			string = string.lower()

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

		return None

	def stripTS3Chat(string):
		if not re.search("<.*?>.*?: ", string) == None:
			string = re.sub("<.*?>.*?: ","", string)
			return string
		return None

	#
	#convenient
	#

	def getNumberBetween(number, min, max):
		if number < min:
			return min
		elif number > max:
			return max
		else:
			return number

	def getNumberFromString(self, string):
		try:
			num = float(string)
		except:
			self.report("not a number")
			return None
		return num

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
		if "https://youtu.be/" in url or "https://www.youtube.com/watch?v=" in url:
			return True
		else:
			self.report(url + " is no valid youtube url")
			return False

	def getYoutubeSongFromString(self, string):
		try:
			query = urllib.parse.quote(string)
			url = "https://www.youtube.com/results?search_query=" + query
			response = urllib.request.urlopen(url)
			html = response.read()
			soup = BeautifulSoup(html, "html.parser")

			for vid in soup.findAll(attrs={"class":"yt-uix-tile-link"}):
				youtubeUrl = "https://www.youtube.com" + vid["href"]
				title = vid["title"]
				if self.isYoutubeURL(youtubeUrl):
					song = Song(youtubeUrl, title=title)
					return song
		except:
			self.report("couldn't find youtube song")
		
		return None
	
	def getYoutubeSongFromPlayCommand(self, command):
		if self.isURL(command.args[0].name):
			url = self.getURL(command.args[0].name)
			if self.isYoutubeURL(url):
				title = getTitleFromYoutubeURL(url)
				song = Song(url, title=title)
				return song
			else:
				self.report("specified value is no youtube url")
		else:
			string = ""
			for arg in command.args:
				string += arg.name + " "

			song = self.getYoutubeSongFromString(string)
			
			if not song == None:
				return song
			else:
				self.report("couldn't find any youtube song")
		
		return None

	def getYoutubeSongFromPlaylistCommand(self, command):
		if isURL(command.args[0].value):
			url = self.getURL(command.args[0].value)
			if isYoutubeURL(url):
				title = getTitleFromYoutubeURL(url)
				song = Song(url, title=title)
				return song
			else:
				self.report("specified value is no youtube url")
		else:
			string = command.args[0].value + " "
			newArgs = command.args[1:]

			for arg in newArgs:
				string += arg.name + " "

			song = self.getYoutubeSongFromString(string)
			
			if not song == None:
				return song
			else:
				self.report("couldn't find any youtube song")
		
		return None

	def getTitleFromYoutubeURL(self, url):
		try:
			response = urllib.request.urlopen(url)
			html = response.read()
			soup = BeautifulSoup(html, "html.parser")
			vid = soup.find(attrs={"class":"yt-uix-tile-link"})
			title = vid["title"]

			return title
		except:
			self.report("couldn't get title from youtube url")

		return None

	#
	#queue
	#

	def play(self, command):
		if len(command.args) > 0:
			song = self.getYoutubeSongFromPlayCommand(command)
			if not song == None:
				bot.play(song)
		else:
			bot.play()

	def playNext(self, command):
		if len(command.args) > 0:
			song = self.getYoutubeSongFromPlayCommand(command)
			if not song == None:
				bot.playNext(song)
		else:
			self.report("not enough Args")

	def playNow(self, command):
		if len(command.args) > 0:
			song = self.getYoutubeSongFromPlayCommand(command)
			if not song == None:
				bot.playNow(song)
		else:
			self.report("not enough Args")

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

		msg = "queue:\n"
		for s in bot.songQueue:
			if index == bot.index:
				msg += ">"
			else:
				msg += " "
			msg += " (" + str(index) + ") " + s.title + " [url=" + s.url + "]URL[/url]\n"
			
			index += 1
		self.report(msg)

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

	def position(self, command):
		if len(command.args) > 0:
			if command.args[0].name.startswith("+"):
				string = command.args[0].name[1:]
				position = self.getNumberFromString(string)
				
				if not position == None:
					bot.plusPosition(position)

			elif command.args[0].name.startswith("-"):
				string = command.args[0].name[1:]
				position = self.getNumberFromString(string)
				
				if not position == None:
					bot.minusPosition(position)

			else:
				position = self.getNumberFromString(command.args[0].name)
				if not position == None:
					bot.setPosition(position)

	def speed(self, command):
		if len(command.args) > 0:
			if command.args[0].name.startswith("+"):
				string = command.args[0].name[1:]
				speed = self.getNumberFromString(string)
				
				if not speed == None:
					bot.plusSpeed(speed)

			elif command.args[0].name.startswith("-"):
				string = command.args[0].name[1:]
				speed = self.getNumberFromString(string)
				
				if not speed == None:
					bot.minusSpeed(speed)

			else:
				speed = self.getNumberFromString(command.args[0].name)
				if not speed == None:
					bot.setSpeed(speed)

	def volume(self, command):
		if len(command.args) > 0:
			if command.args[0].name.startswith("+"):
				string = command.args[0].name[1:]
				volume = int(self.getNumberFromString(string))
				
				if not volume == None:
					bot.plusVolume(volume)

			elif command.args[0].name.startswith("-"):
				string = command.args[0].name[1:]
				volume = int(self.getNumberFromString(string))
				
				if not volume == None:
					bot.minusVolume(volume)

			else:
				volume = int(self.getNumberFromString(command.args[0].name))
				if not volume == None:
					bot.setVolume(volume)

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
						bot.playlistCreateFrom(name, p)
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
							title = getTitleFromYoutubeURL(url)
							song = Song(url, title=title)
							bot.playlistAdd(song, p)
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
				msg = self.playlistListPlaylist(p)
				self.report(msg)
			else:
				self.report("playlist not found")

	def playlistListAll(self):
		msg = "playlists:\n"
		for p in bot.playlists:
			msg += "\n"
			msg += self.playlistListPlaylist(p)

		self.report(msg)

	def playlistListPlaylist(self, playlist):
		index = 0
		msg = playlist.name + "\n"
		for s in playlist.songs:
			msg += "(" + str(index) + ") " + s.title + " [url=" + s.url + "]URL[/url]\n"
			index += 1

		return msg