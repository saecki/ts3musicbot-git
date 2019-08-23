import json
import os
import pafy
import random
import threading
import time
import vlc

from common.classproperties import FileSystem
from common.classproperties import Playlist
from common.classproperties import Song
from common.constants import ForbiddenNames
from common.constants import JSONFields
from common.constants import Modules
from modules import cli
from modules import teamspeak

Instance = None
player = None

modules = []

playlists = []
songQueue = []
index = 0
repeatSong = 0

threads = []
lock = None
clientQueryLock = None

running = True

def run(args= Modules.Teamspeak + Modules.CLI):
	global loop
	global lock
	global clientQueryLock
	global terminalOnly

	if not createVlcPlayer():
		exit()

	readData()

	lock = threading.Lock()
	clientQueryLock = threading.Lock()

	mainThread = addThread(target=mainLoop)
	addThread(target=frequentlyWriteData, daemon=True)

	if Modules.Teamspeak in args:
		modules.append(teamspeak)

	if Modules.CLI in args:
		modules.append(cli)

	for m in modules:
		m.run()

	startThreads()

	report("ready")

	mainThread.join()

def quit():
	global running

	report("exiting")
	writeData()
	running = False
	exit()

def startNewThread(target=None, args=None, daemon=False):
	t = createThread(target=target, args=args, daemon=daemon)
	if t != None:
		t.start()

	return t

def addThread(target=None, args=None, daemon=False):
	t = createThread(target=target, args=args, daemon=daemon)
	if t != None:
		threads.append(t)

	return t

def createThread(target=None, args=None, daemon=False):
	if target != None:
		t = None
		if args == None:
			t = threading.Thread(target=target)
		else:
			t = threading.Thread(target=target, args=args)
		t.setDaemon(daemon)

		return t
	return None

def startThreads():
	for t in threads:
		t.start()

def mainLoop():
	global lastLine
	global index

	while running:

		for m in modules:
			m.update()

		if player.get_state() == vlc.State.Ended:
			if repeatSong == 0:
				next()
			elif repeatSong == 1:
				playSong()
			elif repeatSong == 2:
				if index >= len(songQueue) - 1:
					index = 0
					playSong()
				else:
					next()
		time.sleep(0.5)

def frequentlyWriteData():
	while running:
		with lock:
			writeData()
		time.sleep(600)

def report(string):
	for m in modules:
		m.report(string)

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

#
#file system
#

def writeData():

	data = {}
	data[JSONFields.Playlists] = []
	data[JSONFields.SongQueue] = []
	data[JSONFields.Index] = index
	data[JSONFields.RepeatSong] = repeatSong

	for p in playlists:
		data[JSONFields.Playlists].append(p.toJSON())

	for s in songQueue:
		data[JSONFields.SongQueue].append(s.toJSON())

	try:
		with open(FileSystem.getConfigFilePath(), "w") as jsonfile:
			json.dump(data, jsonfile, indent=4)
	except:
		report("couldn't write data")

def readData():
	global playlists
	global index
	global repeatSong

	try:
		with open(FileSystem.getConfigFilePath()) as jsonfile:
			data = json.load(jsonfile)
			try:
				for p in data[JSONFields.Playlists]:
					playlists.append(Playlist.jsonToPlaylist(p))
			except:
				report("couldn't read playlists")

			try:
				for s in data[JSONFields.SongQueue]:
					songQueue.append(Song.jsonToSong(s))
			except:
				report("couldn't read songQueue")
			
			try:
				index = data[JSONFields.Index]
				if index >= len(songQueue):
					index = len(songQueue - 1)
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
			os.mkdir(FileSystem.getConfigFolderPath())
		except FileExistsError:	
			report("config folder existed")
	return False

#
#getters
#

def getCurrentSong():
	if isPlayingOrPaused() and index < len(songQueue):
		return songQueue[index]
	else:
		return None

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
		song = songQueue[index]
		startNewThread(target=playAudioFromSong, args=(song,), daemon=True)
	else:
		report("there is nothing to play")
def playAudioFromSong(song):
	try:
		playurl = getBestYoutubeAudioURL(song.url)
		
		Media = Instance.media_new(playurl)
		Media.get_mrl()
		player.set_media(Media)
		player.play()
		report("playing " + song.title + " [url=" + song.url + "]URL[/url]")
	except:
		createVlcPlayer()
		report("couldn't play song " + song.title + " [url=" + song.url + "]URL[/url]")

def isPlayingOrPaused():
	if player.get_state() == vlc.State.Playing or player.get_state() == vlc.State.Paused:
		return True
	return False

def setPosition(position):
	position = getNumberBetween(position, 0, 100)
	position = position / 100

	try:
		for i in range(0, 5):
			if player.set_position(position) == None: #Should be checking for 0 but this library is shit and returns None
				time.sleep(0.1)
				report("set position to " + str(round(player.get_position() * 100)) + "%")
				return
	except:
		pass
	report("couldn't update position")

def plusPosition(position):
	setPosition(player.get_position() * 100 + position)

def minusPosition(position):
	setPosition(player.get_position() * 100 - position)

def setSpeed(speed):
	rate = getNumberBetween(speed, 25, 400)
	rate = rate / 100

	try:
		for i in range(0, 5):
			if player.set_rate(rate) == 0:
				time.sleep(0.1)
				report("set speed to " + str(round(player.get_rate() * 100)) + "%")
				return
	except:
		pass
	report("couldn't update speed")

def plusSpeed(speed):
	setSpeed(player.get_rate() * 100 + speed)

def minusSpeed(speed):
	setSpeed(player.get_rate() * 100 - speed)

def setVolume(volume):
	try:
		for i in range(0, 5):
			if player.audio_set_volume(getNumberBetween(volume, 0, 130)) == 0:
				time.sleep(0.1)
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

def play(song=None):
	if song == None:
		if player.get_state() == vlc.State.Paused:
			player.play()
			report("resumed")
		elif player.get_state() != vlc.State.Playing:
			playSong()
		else:
			report("already playing")
	else:
		songQueue.append(song)
		report("added " + song.title + " [url=" + song.url + "]URL[/url] to the queue")
		
		if len(songQueue) == 1:
			playSong()
		elif not (isPlayingOrPaused()):
			next()

def playNext(song):
	songQueue.insert(index + 1, song)
	report("added " + song.title + " [url=" + song.url + "]URL[/url] as next song to the queue")

def playNow(song):
	songQueue.insert(index + 1, song)
	if len(songQueue) == 1:
		playSong()
	else:
		next()

def playQueue(i):
	global index

	index = getNumberBetween(i, 0, len(songQueue) - 1)
	playSong()

def remove(i):
	global index

	if len(songQueue) > 0:
		i = getNumberBetween(i, 0, len(songQueue) - 1)
		
		if i == index:
			removeCurrent()
		else:
			title = songQueue[i].title

			del songQueue[i]
			if i < index:
				index -= 1
			report("removed song " + title + " at index " + str(i) + " from the queue")
	else:
		report("no songs to remove")

def removeNext():
	if index < len(songQueue) - 1:
		title = songQueue[index + 1].title

		del songQueue[index + 1]
		report("removed next song " + title + " from the queue")
	else:
		report("already playing last song")

def removeCurrent():
	global index

	if len(songQueue) > 0:
		title = songQueue[index].title

		del songQueue[index]
		report("removed current song " + title + " from the queue")
		if index >= len(songQueue) and index != 0:
			index = len(songQueue) - 1
			if isPlayingOrPaused():
				stop()
		elif isPlayingOrPaused():
			playSong()
	else:
		report("no songs to remove")

def pause():
	if not player.get_state() == vlc.State.Paused:
		player.pause()
		report("paused")
	else:
		report("already paused")

def toggle():
	if player.get_state() == vlc.State.Playing:
		player.pause()
		report("paused")
	else:
		player.play()
		report("resumed")

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
	fixedSong = songQueue[index]
	fixedIndex = index

	random.shuffle(songQueue)

	newIndex = songQueue.index(fixedSong)
	songQueue[fixedIndex], songQueue[newIndex] = songQueue[newIndex], songQueue[fixedIndex]

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

def playlistCreateFromQueue(name):
	if not isForbidden(name):
		p = Playlist(name)
		p.songs = songQueue.copy()
		playlists.append(p)
		report("created " + name + " from the queue")

def playlistCreateFrom(name, playlist):
	if not isForbidden(name):
		p = Playlist(name)
		p.songs = playlist.songs.copy()
		playlists.append(p)
		report("created " + name + " from " + playlist.name)

def isForbidden(name):
	for f in ForbiddenNames.fields:
		for n in f:
			if name == n:
				report("name is forbidden")
				return True
	for p in playlists:
		if name == p.name:
			report("name already exists")
			return True
	return False

def playlistDelete(playlist):
	playlists.remove(playlist)
	report("deleted " + playlist.name)

def playlistAdd(song, playlist):
	playlist.addSong(songURL)
	report("added " + song.title + "to " + playlist.name)

def playlistRemove(index, playlist):
	index = getNumberBetween(index, 0, len(songQueue) - 1)
	del playlist.songs[index]
	report("removed song at index " + str(index) + " from " + playlist.name)

def playlistPlay(playlist):
	global songQueue
	global index

	songQueue = playlist.songs.copy()
	index = 0
	report("replaced the queue with " + playlist.name)
	playSong()

def playlistQueue(playlist):
	global songQueue

	songQueue = songQueue + playlist.songs
	report("added songs from " + playlist.name + " to the queue")
	if (player.get_state() != vlc.State.Playing or player.get_state() == vlc.State.Paused):
		playSong()

def playlistShuffle(playlist):
	random.shuffle(playlist.songs)
	report("shuffled " + playlist.name)

def playlistClear(playlist):
	playlist.songs.clear()
	report("cleared " + playlist.name)