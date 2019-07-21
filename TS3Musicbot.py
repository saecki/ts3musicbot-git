import pafy
import vlc
import os
import asyncio
import time
import json
import re
import random
import urllib.request
from bs4 import BeautifulSoup

class Commands:
	play = "!play"
	playNext = "!playnext"
	playNow = "!playnow"
	playQueue = "!playqueue"
	pause = "!pause"
	next = "!next"
	previous = "!prev"
	stop = "!stop"
	clear = "!clear"
	shuffle = "!shuffle"
	list = "!list"

	repeat = "!repeat"
	repeatAll = "all"
	repeatStop = "stop"

	playlist = "!playlist"
	playlistCreate = "create:"
	playlistFrom = "from:"
	playlistAdd = "add:"
	playlistTo = "to:"
	playlistDelete = "delete:"
	playlistPlay = "play:"
	playlistQueue = "queue:"
	playlistShuffle = "shuffle:"
	playlistClear = "clear:"
	playlistList = "list"

class Command:

	def __init__(self, name):
		self.name = name
		self.args = []

class Argument:

	def __init__(self, name, value = None):
		self.name = name
		self.value = value

class Playlist:

	def __init__(self, name):
		self.name = name
		self.songURLs = []

	def addSong(self, songURL):
		self.songURLs.append(songURL)

	def toJSON(self):
		playlist = {}
		playlist["name"] = self.name
		playlist["songURLs"] = []
		for songURL in self.songURLs:
			playlist["songURLs"].append({"songURL": songURL})

		return playlist

def jsonToPlaylist(json):
	playlist = Playlist(json["name"])
	for songURL in json["songURLs"]:
		playlist.addSong(songURL["songURL"])

	return playlist

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

	all_subdirs = getAllSubdirsOf(p)
	latest_subdir = max(all_subdirs, key=os.path.getmtime)

	path = latest_subdir
	path += os.path.sep
	path += "channel.txt"

	return path

def getConfigFolderPath():
	path = os.getenv("APPDATA")
	path += os.path.sep
	path += "TS3MusicBot"

	return path

def getConfigFilePath():
	path = getConfigFolderPath()
	if len(path) > 0:
		path += os.path.sep
	path += "config.json"

	return path

def getAllSubdirsOf(b="."):
	result = []
	for d in os.listdir(b):
		bd = os.path.join(b, d)
		if os.path.isdir(bd): result.append(bd)
	return result

def getFileLineCount(path):
    return sum(1 for line in open(path))

def writeData():

	data = {}
	data["playlists"] = []

	for p in playlists:
		data["playlists"].append(p.toJSON())
	try:
		with open(getConfigFilePath(), "w") as jsonfile:
			json.dump(data, jsonfile)
	except:
		print("couldn't write data")

def readData():
	global playlists

	try:
		with open(getConfigFilePath()) as jsonfile:  
			data = json.load(jsonfile)
			for p in data["playlists"]:
				playlists.append(jsonToPlaylist(p))

	except:
		print("couldn't read config file")

		#trying to create the conifg folder
		try:
			os.mkdir(getConfigFolderPath())
		except FileExistsError:	
			print("config folder existed")

#
#url
#

def isURL(string):
	if "[URL]" in string and "[/URL]" in string:
		return True
	else:
		return False

def getURL(string):
	url = string
	url = url.replace("[URL]", "")
	url = url.replace("[/URL]", "")

	return url

def isYoutubeURL(url):
	if "youtu.be" in url or "youtube.com" in url:
		return True
	else:
		print("no valid youtube link")
		return False

def getBestYoutubeAudioURL(url):
	video = pafy.new(url)
	best = video.getbestaudio()
	playurl = best.url

	return playurl

def getYoutubeURLFromString(string):
	
	query = urllib.parse.quote(string)
	url = "https://www.youtube.com/results?search_query=" + query
	response = urllib.request.urlopen(url)
	html = response.read()
	soup = BeautifulSoup(html, 'html.parser')
	
	for vid in soup.findAll(attrs={'class':'yt-uix-tile-link'}):
		return 'https://www.youtube.com' + vid['href']
	return None

#
#playback
#

def createVlcPlayer():
	global Instance
	global player

	Instance = vlc.Instance()
	player = Instance.media_player_new()

def playSong():
	if index < len(songQueue):
		playAudioFromUrl(songQueue[index])

def playAudioFromUrl(url):

	try:
		playurl = getBestYoutubeAudioURL(url)
		
		Media = Instance.media_new(playurl)
		Media.get_mrl()
		player.set_media(Media)
		player.play()
		print("playing " + url)
	except:
		createVlcPlayer()
		print("couldn't play song with url " + url)

#
#queue
#

def play(command):
	if len(command.args) > 0:
		url = getYoutubeURLFromCommand(command)
		
		if not url == None:
			songQueue.append(url)
			print("added " + url + " to the queue")
			if not (player.get_state() == vlc.State.Playing or player.get_state() == vlc.State.Paused or len(songQueue) == 1):
				next()
			
			if len(songQueue) == 1:
				playSong()

	elif player.get_state() == vlc.State.Paused:
		player.play()
		print("resumed")
	else:
		playSong()

def playNext(command):
	if len(command.args) > 0:
		url = getYoutubeURLFromCommand(command)
		
		if not url == None:
			songQueue.insert(index + 1, url)
			print("added " + url + "as next song to the queue")
	else:
		print("not enough arguments")

def playNow(command):
	if len(command.args) > 0:
		url = getYoutubeURLFromCommand(command)
		
		if not url == None:
			songQueue.insert(index + 1, url)
			if len(songQueue) == 1:
				playSong()
			else:
				next()
	else:
		print("not enough arguments")

def playQueue(command):
	global index

	if len(command.args) > 0:
		integer = True

		try:
			tempIndex = int(command.args[0].name)
		except:
			integer = False
			print("enter a valid number as argument")

		if integer:
			index = getNumberBetween(tempIndex, 0, len(songQueue) - 1)
			playSong()
			print("playing queue at index " + str(index))

def getYoutubeURLFromCommand(command):
	if isURL(command.args[0].name):
		url = getURL(command.args[0].name)
		if isYoutubeURL(url):
			return url
		else:
			print("specified value is no youtube url")
	else:
		string = ""
		for arg in command.args:
			string += arg.name + " "

		url = getYoutubeURLFromString(string)
		
		if not url == None:
			return url
		else:
			print("couldn't find any video")
	
	return None

def pause():
	player.pause()
	print("paused")

def previous():
	global index

	if index > 0:
		index -= 1
		print("previous song")
		playSong()
	elif repeatSong == 2:
		index = len(songQueue) - 1
		print("previous song")
		playSong()
	else:
		print("already playing first song")

def next():
	global index

	player.stop()
	if index < len(songQueue) - 1:
		index += 1 
		print("next song")
		playSong()
	elif repeatSong == 2:
		index = 0
		print("next song")
		playSong()
	else:
		print("already played last song")

def stop():
	global index

	player.stop()
	if index < len(songQueue) - 1:
		index += 1
	print("stopped")

def clear():
	stop()
	songQueue.clear()
	index = 0
	print("cleared queue")

def shuffle():
	random.shuffle(songQueue)
	print("shuffled queue")

def list():
	print("queue:")
	for s in songQueue:
		print("   " + s)

def repeat(command):
	global repeatSong

	if len(command.args) > 0:
		if command.args[0].name == Commands.repeatAll:
			repeatSong = 2
			print("repeating all songs")
		elif command.args[0].name == Commands.repeatStop:
			repeatSong = 0
			print("stopped repeating")
		else:
			print("argument " + command.args[0].name + " not found")
	else:
		repeatSong = 1
		print("repeating one song")

#
#playlist
#

def playlist(command):
	if len(command.args) > 0:
		if command.args[0].name == Commands.playlistCreate:
			playlistCreate(command.args)
		elif command.args[0].name == Commands.playlistDelete:
			playlistDelete(command.args)
		elif command.args[0].name == Commands.playlistAdd:
			playlistAdd(command.args)
		elif command.args[0].name == Commands.playlistPlay:
			playlistPlay(command.args)
		elif command.args[0].name == Commands.playlistQueue:
			playlistQueue(command.args)
		elif command.args[0].name == Commands.playlistShuffle:
			playlistShuffle(command.args)
		elif command.args[0].name == Commands.playlistClear:
			playlistClear(command.args)
		elif command.args[0].name == Commands.playlistList:
			playlistList()
		else:
			print("argument " + command.args[0].name + " not found")
		writeData()
	else:
		print("not enough arguments")

def playlistCreate(args):
	if len(args) > 1:
		if args[1].name == Commands.playlistFrom:
			if args[1].value == "queue":
				playlist = Playlist(args[0].value)
				playlist.songURLs = songQueue.copy()
				playlists.append(playlist)
				print("created playlist " + args[0].value + " from queue")
			else:
				for p in playlists:
					if p.name == args[1].value:
						playlist = Playlist(args[0].value)
						playlist.songURLs = p.songURLs.copy()
						playlists.append(playlist)
						print("created playlist " + args[0].value + " from " + args[1].value)
						return
				print("couldn't find playlist")
		else:
			print("specified argument not correct")
	else:
		playlists.append(Playlist(args[0].value))
		print("created playlist " + args[0].value)

def playlistDelete(args):
	for p in playlists:
		if p.name == args[0].value:
			playlists.remove(p)
			print("deleted " + args[0].value)

			return
	print("playlist not found")

def playlistAdd(args):
	if len(args) > 1:
		if args[1].name == Commands.playlistTo:			
			for p in playlists:
				if p.name == args[1].value:					
					if isURL(args[0].value):
						url = getURL(args[0].value)
						if isYoutubeURL(url):
							p.addSong(url)
							print("added " + url + "to " + p.name)
						else:
							print("specified value is no youtube url")
					else:
						print("specified value is no url")
					return
			print("playlist not found")
		else:
			print("specified argument not correct")
	else:
		print("not enough arguments")

def playlistPlay(args):
	global songQueue

	for p in playlists:
		if p.name == args[0].value:
			clear()
			songQueue = p.songURLs.copy()
			print("replaced the queue with " + p.name)
			playSong()

			return
	print("playlist not found")

def playlistQueue(args):
	global songQueue

	for p in playlists:
		if p.name == args[0].value:
			songQueue = songQueue + p.songURLs
			print("added songs from " + p.name + " to the queue")
			if not (player.get_state() == vlc.State.Playing or player.get_state() == vlc.State.Paused):
				playSong()

			return
	print("playlist not found")

def playlistShuffle(args):
	for p in playlists:
		if p.name == args[0].value:
			random.shuffle(p.songURLs)
			print("shuffled playlist")
			return
	print("playlist not found")

def playlistClear(args):
	for p in playlists:
		if p.name == args[0].value:
			p.songURLs.clear()
			print("cleared playlist")
			return
	print("playlist not found")

def playlistList():
	print("playlists:")
	for p in playlists:
		index = 0

		print()
		print(p.name)
		for s in p.songURLs:
			print("(" + str(index) + ")   " + s)
			index += 1

#
#commands
#

def stringToCommand(string):

	string = re.sub("<.*?: ","", string)
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

def handleCommand(string):

	command = stringToCommand(string)

	if not command == None:
		if command.name == Commands.play:
			play(command)
		elif command.name == Commands.playNext:
			playNext(command)
		elif command.name == Commands.playNow:
			playNow(command)
		elif command.name == Commands.playQueue:
			playQueue(command)
		elif command.name == Commands.pause:
			pause()
		elif command.name == Commands.previous:
			previous()
		elif command.name == Commands.next:
			next()
		elif command.name == Commands.stop:
			stop()
		elif command.name == Commands.clear:
			clear()
		elif command.name == Commands.shuffle:
			shuffle()
		elif command.name == Commands.list:
			list()
		elif command.name == Commands.repeat:
			repeat(command)
		elif command.name == Commands.playlist:
			playlist(command)
		else:
			print("the command: " + command.name + " wasn't found")
	else:
		print("wow that's impressive")


async def mainLoop():
	global lastLine
	global index

	while True:
		try:
			currentLine = getFileLineCount(getTS3ChannelChatFilePath())
			if  currentLine > lastLine:
				with open(getTS3ChannelChatFilePath()) as f:
					for line in f:
						pass
					command = line
					handleCommand(command)
					lastLine = currentLine
			elif player.get_state() == vlc.State.Ended:
				if repeatSong == 0:
					next()
				if repeatSong == 1:
					playSong()
				elif repeatSong == 2:
					if index >= len(songQueue) - 1:
						index = 0
						playSong()
					else:
						next()
		except:
			print("error in main loop")

		await asyncio.sleep(0.5)

Instance = None
player = None
createVlcPlayer()

playlists = []

songQueue = []
index = 0
repeatSong = 0

readData()

lastLine = getFileLineCount(getTS3ChannelChatFilePath())

loop = asyncio.get_event_loop()
loop.create_task(mainLoop())

print("Waiting for a command")

try:
	loop.run_forever()
except KeyboardInterrupt:
	pass
finally:
	loop.run_until_complete(loop.shutdown_asyncgens())
	loop.close()

print("Exiting")