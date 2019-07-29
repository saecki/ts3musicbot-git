import pafy
import vlc 
import os
import asyncio
import time
import json
import random

from common.classproperties import TS3MusicBotModule
from common.classproperties import Playlist
from common.constants import Modules
from common.constants import JSONFields
from common.constants import ForbiddenNames

from modules.cli import CLI

Instance = None
player = None

modules = []

playlists = []
songQueue = []
index = 0
repeatSong = 0

loop = None

def run(args=Modules.CLI):
	global loop

	if not createVlcPlayer():
		exit()

	readData()

	loop = asyncio.get_event_loop()
	addTaskToAsyncIOLoop(mainLoop())
	addTaskToAsyncIOLoop(frequentlyWriteData())

	if Modules.CLI in args:
		modules.append(CLI())

	try:
		loop.run_forever()
	except:
		pass
	finally:
		quit()

	report("Exiting")

def end():
	if not loop == None:
		loop.run_until_complete(loop.shutdown_asyncgens())
		loop.close()
		report("stopped TS3MusicBot")
		writeData()

def quit():
	loop.run_until_complete(loop.shutdown_asyncgens())
	loop.close()
	writeData()
	exit()

def addTaskToAsyncIOLoop(function):
	loop.create_task(function)

async def mainLoop():
	global lastLine
	global index

	while True:

		for m in modules:
			m.update()

		if player.get_state() == vlc.State.Ended:
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

		await asyncio.sleep(0.5)

async def frequentlyWriteData():
	while True:
		writeData()
		await asyncio.sleep(600)

def report(string):
	for m in modules:
		m.report(string)

#
#maths stuff
#

def getNumberBetween(number, min, max):
	if number < min:
		return minp
	elif number > max:
		return max
	else:
		return number

#
#file system
#

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

def writeData():

	data = {}
	data[JSONFields.Playlists] = []
	data[JSONFields.SongQueue] = []
	data[JSONFields.Index] = index
	data[JSONFields.RepeatSong] = repeatSong

	for p in playlists:
		data[JSONFields.Playlists].append(p.toJSON())

	for s in songQueue:
		data[JSONFields.SongQueue].append(s)

	try:
		with open(getConfigFilePath(), "w") as jsonfile:
			json.dump(data, jsonfile)
	except:
		report("couldn't write data")

def readData():
	global playlists
	global index
	global repeatSong

	try:
		with open(getConfigFilePath()) as jsonfile:  
			data = json.load(jsonfile)
			try:
				for p in data[JSONFields.Playlists]:
					playlists.append(Playlist.jsonToPlaylist(p))
			except:
				report("couldn't read playlists")

			try:
				for s in data[JSONFields.SongQueue]:
					songQueue.append(s)
			except:
				report("couldn't read songQueue")
			
			try:
				index = data[JSONFields.Index]
			except:
				report("couldn't read index")			
			
			try:
				repeatSong = data[JSONFields.RepeatSong]
			except:
				report("couldn't read repeatSong")
		
		return True
	except:
		report("couldn't read config file")
		report("trying to create the conifg folder")
		try:
			os.mkdir(getConfigFolderPath())
		except FileExistsError:	
			report("config folder existed")
	return False

#
#url
#

def getBestYoutubeAudioURL(url):
	video = pafy.new(url)
	best = video.getbestaudio()
	playurl = best.url

	return playurl

#
#playback
#

def createVlcPlayer():
	global Instance
	global player
	
	for i in range(0, 5):
		try:
			Instance = vlc.Instance()
			player = Instance.media_player_new()
			return True
		except:
			report("couldn't create vlc player in the " + str(i+1) + ". try")
	return False

def playSong():
	if index < len(songQueue):
		playAudioFromUrl(songQueue[index])
	else:
		report("there is nothing to play")

def playAudioFromUrl(url):

	try:
		playurl = getBestYoutubeAudioURL(url)
		
		Media = Instance.media_new(playurl)
		Media.get_mrl()
		player.set_media(Media)
		player.play()
		report("playing " + url)
	except:
		createVlcPlayer()
		report("couldn't play song with url " + url)

def isPlayingOrPaused():
	if player.get_state() == vlc.State.Playing or player.get_state() == vlc.State.Paused:
		return True
	return False

def setVolume(volume):
	try:
		for i in range(0, 5):
			if player.audio_set_volume(getNumberBetween(volume, 0, 120)) == 0:
				time.sleep(200)
				report("set volume to " + str(player.audio_get_volume()))
				return
	except:
		pass
	report("couldn't update volume")

def plusVolume(volume):
	setVolume(player.audio_get_volume() + volume)

def minusVolume(volume):
	setVolume(player.audio_get_volume() - volume)
#
#queue
#

def play(songURL=None):
	if songURL == None:
		if player.get_state() == vlc.State.Paused:
			player.play()
			report("resumed")
		elif not player.get_state() == vlc.State.Playing:
			playSong()
		else:
			report("already playing")
	else:
		songQueue.append(songURL)
		report("added " + songURL + " to the queue")
		
		if len(songQueue) == 1:
			playSong()
		elif not (isPlayingOrPaused()):
			next()

def playNext(songURL):
	songQueue.insert(index + 1, url)
	report("added " + url + "as next song to the queue")

def playNow(songURL):
	songQueue.insert(index + 1, songURL)
	if len(songQueue) == 1:
		playSong()
	else:
		next()

def remove(i):
	global index

	if len(songQueue) > 0:
		i = getNumberBetween(i, 0, len(songQueue) - 1)
		
		if i == index:
			removeCurrent()
		else:
			del songQueue[i]
			if index >= len(songQueue):
				index = len(songQueue) - 1
			report("removed song at index " + str(i) + " from the queue")
	else:
		report("no songs to remove")

def removeNext():
	if index < len(songQueue) - 1:
		del songQueue[index + 1]
		report("removed next song from the queue")
	else:
		report("already playling last song")

def removeCurrent():
	global index

	if len(songQueue) > 0:
		del songQueue[index]
		report("removed current song from the queue")
		if index >= len(songQueue) and not index == 0:
			index = len(songQueue) - 1
			if isPlayingOrPaused():
				stop()
		elif isPlayingOrPaused():
			playSong()
	else:
		report("no songs to remove")

def playQueue(i):
	global index

	index = getNumberBetween(i, 0, len(songQueue) - 1)
	playSong()
	report("playing queue at index " + str(i))

def pause():
	player.pause()
	report("paused")

def previous():
	global index

	if index > 0:
		index -= 1
		report("previous song")
		playSong()
	elif repeatSong == 2:
		index = len(songQueue) - 1
		report("previous song")
		playSong()
	else:
		report("already playing first song")

def next():
	global index

	player.stop()
	if index < len(songQueue) - 1:
		index += 1 
		report("next song")
		playSong()
	elif repeatSong == 2:
		index = 0
		report("next song")
		playSong()
	else:
		report("already played last song")

def stop():
	global index

	player.stop()
	if index < len(songQueue) - 1:
		index += 1
	report("stopped")

def clear():
	global index

	stop()
	songQueue.clear()
	index = 0
	report("cleared queue")

def shuffle():
	random.shuffle(songQueue)
	report("shuffled queue")

def repeat(mode):
	global repeatSong

	repeatSong = getNumberBetween(mode, 0, 2)

	if repeatSong == 0:
		report("stopped repeating")
	elif repeatSong == 1:
		report("repeating one song")
	else:
		report("repeating all songs")

#
#playlist
#

def getPlaylist(name):
	for p in playlists:
		if p.name == name:
			return p
	return None

def playlistCreate(name):
	if not isForbidden(name):
		p = Playlist(name)
		playlists.append(p)
		report("created " + name)
		writeData()

def playlistCreateFromQueue(name):
	if not isForbidden(name):
		p = Playlist(name)
		p.songURLs = songQueue.copy()
		playlists.append(p)
		report("created " + name + " from the queue")
		writeData()

def playlistCreateFrom(name, playlist):
	if not isForbidden(name):
		p = Playlist(name)
		p.songURLs = playlist.songURLs.copy()
		playlists.append(p)
		report("created " + name + " from " + playlist.name)
		writeData()

def isForbidden(name):
	for n in ForbiddenNames.fields:
		if name == n:
			report("name is forbidden")
			return True
	for p in playlists:
		if name == p.name:
			report("name is already exists")
			return True
	return False

def playlistDelete(playlist):
	playlists.remove(playlist)
	report("deleted " + playlist.name)
	writeData()

def playlistAdd(songURL, playlist):
	playlist.addSong(songURL)
	report("added " + songURL + "to " + playlist.name)
	writeData()

def playlistRemove(index, playlist):
	index = getNumberBetween(index, 0, len(songQueue) - 1)
	del playlist.songURLs[index]
	report("removed song at index " + str(index) + " from " + playlist.name)
	writeData()

def playlistPlay(playlist):
	global songQueue
	global index

	songQueue = playlist.songURLs.copy()
	index = 0
	report("replaced the queue with " + playlist.name)
	playSong()

def playlistQueue(playlist):
	global songQueue

	songQueue = songQueue + playlist.songURLs
	report("added songs from " + playlist.name + " to the queue")
	if not (player.get_state() == vlc.State.Playing or player.get_state() == vlc.State.Paused):
		playSong()

def playlistShuffle(playlist):
	random.shuffle(playlist.songURLs)
	report("shuffled " + playlist.name)
	writeData()

def playlistClear(playlist):
	playlist.songURLs.clear()
	report("cleared " + playlist.name)
	writeData()