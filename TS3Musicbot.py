import pafy
import vlc
import os
import asyncio
import time
import json

class Playlist:

	songURLs = []

	def __init__(self, name):
		self.name = name

	def addSong(songURL):
		self.songURLs.append(songURL)

	def toJSON():
		playlist = {}
		playlist["name"] = self.name
		playlist["songURLs"] = []
		for songURL in songURLs:
			playlist["songURLs"].append({"songURL": song})

		return playlist

def jsonToPlaylist(json):
	playlist = Playlist(json["name"])
	for songURL in json["songURLs"]:
		playlist.addSong(songURL["songURL"])

	return playlist

Instance = vlc.Instance()
player = Instance.media_player_new()

def getAllSubdirsOf(b='.'):
	result = []
	for d in os.listdir(b):
		bd = os.path.join(b, d)
		if os.path.isdir(bd): result.append(bd)
	return result

def getTS3ChannelChatFilePath():
	p = os.getenv('APPDATA')
	p += os.path.sep
	p += "TS3Client\\chats"

	all_subdirs = getAllSubdirsOf(p)
	latest_subdir = max(all_subdirs, key=os.path.getmtime)

	path = latest_subdir
	path += os.path.sep
	path += "channel.txt"

	return path

def getFileLineCount(path):
    return sum(1 for line in open(path))

def playNextSong():
	if index < len(queue):
		playAudioFromUrl(queue[index])

def playAudioFromUrl(url):
	video = pafy.new(url)
	best = video.getbest()
	playurl = best.url
	
	Media = Instance.media_new(playurl)
	Media.get_mrl()
	player.set_media(Media)
	player.play()
	print("playing " + url)

def handleCommand(command):

	print(command)

	if "!playqueue" in command:
		playQueue(command)
	elif "!play" in command:
		play(command)
	elif "!pause" in command:
		pause()
	elif "!stop" in command:
		stop()
	elif "!prev" in command:
		previous()
	elif "!next" in command:
		next()
	elif "!seek" in command:
		seek(command)
	else:
		print("The command: " + command + "has a wrong syntax")

def play(command):
	tempurl = command
	tempurl = tempurl.replace("[URL]", "") 
	tempurl = tempurl.replace("[/URL]", "")
	l = tempurl.split("!play ", 1)
	if len(l) > 1:
		url = l[1]
		queue.append(url)
		print("added " + url + "to the queue")
	else:
		player.play()
		print("resumed")

def playQueue(command):
	global index
	l = command.split("!playqueue ", 1)
	if len(l) > 1:
		tempindex = int(l[1]) - 1
		if tempindex >= 0 and tempindex < len(queue):
			index = tempindex
			playNextSong()
			print("playing queue at index " + str(index))
		else:
			print("index out of bounds")

def pause():
	player.pause()
	print("paused")

def stop():
	player.stop()
	print("stopped")

def previous():
	global index
	if index > 0:
		player.stop()
		index -= 1
		print("previous song")
		playNextSong()
	else:
		print("already playing first song")

def next():
	global index
	player.stop()
	if index < len(queue) - 1:
		index += 1 
		print("next song")
		playNextSong()
	else:
		print("already playing last song")

def seek(command):
	pass

async def mainLoop():
	global lastLine
	while True:
		currentLine = getFileLineCount(getTS3ChannelChatFilePath())
		if  currentLine > lastLine:
			lastLine = currentLine
			with open(getTS3ChannelChatFilePath()) as f:
				for line in f:
					pass
				command = line
				handleCommand(command)

		if player.get_state() == vlc.State.NothingSpecial:
			playNextSong()
		elif player.get_state() == vlc.State.Ended:
			next()

		await asyncio.sleep(0.5)

playlists = []

queue = []
index = 0

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
