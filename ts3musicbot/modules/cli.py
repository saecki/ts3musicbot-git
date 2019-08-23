import time
import urllib.request
import vlc

from bs4 import BeautifulSoup

import ts3musicbot as bot

from common.classproperties import Argument
from common.classproperties import Command
from common.classproperties import Playlist
from common.classproperties import Song
from common.constants import ArgValues
from common.constants import Args
from common.constants import Commands
from common.constants import Prefixes

def run():
	bot.addThread(target=startCheckingForTerminalCommand, daemon=True)

def update():
	pass

def report(string):
	print(string)

#
#terminal
#

def startCheckingForTerminalCommand():
	while bot.running:
		try:
			string = input()
		except:
			print("terminal input failed")
		else:
			if string == "exit":
				bot.quit()
			command = stringToCommand(string)
			with bot.lock:
				handleCommand(command)

#
#commands
#

def handleCommand(command, prefix=("",)):
	if command != None:
		startswithprefix = None
		for p in prefix:
			if command.name.startswith(p):
				startswithprefix = p
				break

		if startswithprefix != None:
			command.name = command.name[len(startswithprefix):]
			if command.name in Commands.Play:
				play(command)
			elif command.name in Commands.PlayNext:
				playNext(command)
			elif command.name in Commands.PlayNow:
				playNow(command)
			elif command.name in Commands.PlayQueue:
				playQueue(command)
			elif command.name in Commands.Remove:
				remove(command)
			elif command.name in Commands.RemoveNext:
				removeNext()
			elif command.name in Commands.RemoveCurrent:
				removeCurrent()
			elif command.name in Commands.Pause:
				pause()
			elif command.name in Commands.Toggle:
				toggle()
			elif command.name in Commands.Previous:
				previous()
			elif command.name in Commands.Next:
				next()
			elif command.name in Commands.Stop:
				stop()
			elif command.name in Commands.Clear:
				clear()
			elif command.name in Commands.Shuffle:
				shuffle()
			elif command.name in Commands.Repeat:
				repeat(command)
			elif command.name in Commands.List:
				list()
			elif command.name in Commands.Position:
				position(command)				
			elif command.name in Commands.Speed:
				speed(command)
			elif command.name in Commands.Volume:
				volume(command)
			elif command.name in Commands.Lyrics:
				lyrics(command)
			elif command.name in Commands.Status:
				status()
			elif command.name in Commands.Playlist:
				playlist(command)
			else:
				bot.report("the command: " + command.name + " wasn't found")
		else:
			bot.report("prefix not found")
	else:
		bot.report("wow that's impressive")

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

#
#convenient
#

def getNumberFromString(string):
	try:
		num = float(string)
	except:
		bot.report("not a number")
		return None
	return num

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
	if "https://youtu.be/" in url or "https://www.youtube.com/watch?v=" in url:
		return True
	else:
		return False

def getCommandArgsAsString(args, start=0, end=None, till=None):
	msg = ""

	length = len(args)

	if end == None:
		end = length

	if length > start and length >= end:
		for i in range(start, end):
			n = args[i].name
			if n == till:
				break
			else:
				msg += n + " "

			v = args[i].value
			if v != None:
				if v == till:
					break
				else:
					msg += v + " " 

	return msg


def getYoutubeSongFromString(string):
	try:
		query = urllib.parse.quote(string)
		url = "https://www.youtube.com/results?search_query=" + query
		response = urllib.request.urlopen(url)
		html = response.read()
		soup = BeautifulSoup(html, "html.parser")

		for vid in soup.findAll(attrs={"class":"yt-uix-tile-link"}):
			youtubeUrl = "https://www.youtube.com" + vid["href"]
			title = vid["title"]
			if isYoutubeURL(youtubeUrl):
				song = Song(youtubeUrl, title=title)
				return song
	except:
		bot.report("couldn't find youtube song")
	
	return None

def getYoutubeSongFromPlayCommand(command):
	if isURL(command.args[0].name):
		url = getURL(command.args[0].name)
		if isYoutubeURL(url):
			title = getTitleFromYoutubeURL(url)
			song = Song(url, title=title)
			return song
		else:
			bot.report(url + " is no valid youtube url")
	else:
		string = ""
		for arg in command.args:
			string += arg.name + " "

		song = getYoutubeSongFromString(string)
		
		if song != None:
			return song
		else:
			bot.report("couldn't find any youtube song")
	
	return None

def getYoutubeSongFromPlaylistCommand(command):
	if isURL(command.args[0].value):
		url = getURL(command.args[0].value)
		if isYoutubeURL(url):
			title = getTitleFromYoutubeURL(url)
			song = Song(url, title=title)
			return song
		else:
			bot.report(url + " is no valid youtube url")
	else:
		string = command.args[0].value + " "
		newArgs = command.args[1:]

		for arg in newArgs:
			string += arg.name + " "

		song = getYoutubeSongFromString(string)
		
		if song != None:
			return song
		else:
			bot.report("couldn't find any youtube song")
	
	return None

def getTitleFromYoutubeURL(url):
	try:
		response = urllib.request.urlopen(url)
		html = response.read()
		soup = BeautifulSoup(html, "html.parser")
		vid = soup.find(attrs={"class":"yt-uix-tile-link"})
		title = vid["title"]

		return title
	except:
		bot.report("couldn't get title from youtube url")

	return None

#
#strings
#

def getStatus():
	msg = "status:\n"
	msg += "playback state: " + str(bot.player.get_state()) + "\n"
	if getCurrentSongTitle() != None:
		msg += "title: " + getCurrentSongTitle() + "\n"
		msg += "position: " +  getPosition() + "\n"
	msg += "speed: " + getSpeed() + "\n"
	msg += "volume : " + getVolume() + "\n"
	msg += "index: " + str(bot.index) + "\n"
	msg += "songQueue length: " + str(len(bot.songQueue)) + "\n"

	return msg

def getPlaybackInfo():
	msg = ""

	if len(bot.songQueue) > 0:
		msg = bot.songQueue[bot.index].title
		
		if bot.player.get_state() == vlc.State.Playing:
			msg = "playing: " + msg
		elif bot.player.get_state() == vlc.State.Paused:
			msg = "paused: " + msg
		else:
			msg = ""

		if bot.player.is_seekable():
				msg += " | " + getPosition()

	return msg

def getCurrentSongTitle():
	song = bot.getCurrentSong()
	if song != None:
		return song.title
	return None

def getPosition():
	return str(round(bot.player.get_rate() * 100)) + "%"

def getSpeed():
	return str(round(bot.player.get_rate() * 100)) + "%"

def getVolume():
	return str(bot.player.audio_get_volume()) + "%"

#
#queue
#

def play(command):
	if len(command.args) > 0:
		song = getYoutubeSongFromPlayCommand(command)
		if song != None:
			bot.play(song)
	else:
		bot.play()

def playNext(command):
	if len(command.args) > 0:
		song = getYoutubeSongFromPlayCommand(command)
		if song != None:
			bot.playNext(song)
	else:
		bot.report("not enough Args")

def playNow(command):
	if len(command.args) > 0:
		song = getYoutubeSongFromPlayCommand(command)
		if song != None:
			bot.playNow(song)
	else:
		bot.report("not enough Args")

def playQueue(command):
	if len(command.args) > 0:
		integer = True

		try:
			index = int(command.args[0].name)
		except:
			integer = False
			bot.report("enter a valid number as argument")

		if integer:
			bot.playQueue(index)

def remove(command):
	if len(command.args) > 0:
		integer = True

		try:
			index = int(command.args[0].name)
		except:
			integer = False
			bot.report("enter a valid number as argument")

		if integer:
			bot.remove(index)

def removeNext():
	bot.removeNext()

def removeCurrent():
	bot.removeCurrent()

def pause():
	bot.pause()

def toggle():
	bot.toggle()

def previous():
	bot.previous()

def next():
	bot.next()

def stop():
	bot.stop()

def clear():
	bot.clear()

def shuffle():
	bot.shuffle()

def list():
	index = 0

	msg = "queue:\n"
	for s in bot.songQueue:
		if index == bot.index:
			msg += ">"
		else:
			msg += " "
		msg += " (" + str(index) + ") " + s.title + " [url=" + s.url + "]URL[/url]\n"
		
		index += 1
	bot.report(msg)

def repeat(command):
	if len(command.args) > 0:
		if command.args[0].name in ArgValues.All:
			bot.repeat(2)
		elif command.args[0].name in ArgValues.Stop:
			bot.repeat(0)
		else:
			bot.report("argument " + command.args[0].name + " not found")
	else:
		bot.repeat(1)

def position(command):
	if len(command.args) > 0:
		if command.args[0].name.startswith("+"):
			string = command.args[0].name[1:]
			position = getNumberFromString(string)
			
			if position != None:
				bot.plusPosition(position)

		elif command.args[0].name.startswith("-"):
			string = command.args[0].name[1:]
			position = getNumberFromString(string)
			
			if position != None:
				bot.minusPosition(position)

		else:
			position = getNumberFromString(command.args[0].name)
			if position != None:
				bot.setPosition(position)

def speed(command):
	if len(command.args) > 0:
		if command.args[0].name.startswith("+"):
			string = command.args[0].name[1:]
			speed = getNumberFromString(string)
			
			if speed != None:
				bot.plusSpeed(speed)

		elif command.args[0].name.startswith("-"):
			string = command.args[0].name[1:]
			speed = getNumberFromString(string)
			
			if speed != None:
				bot.minusSpeed(speed)

		else:
			speed = getNumberFromString(command.args[0].name)
			if speed != None:
				bot.setSpeed(speed)

def volume(command):
	if len(command.args) > 0:
		if command.args[0].name.startswith("+"):
			string = command.args[0].name[1:]
			volume = int(getNumberFromString(string))
			
			if volume != None:
				bot.plusVolume(volume)

		elif command.args[0].name.startswith("-"):
			string = command.args[0].name[1:]
			volume = int(getNumberFromString(string))
			
			if volume != None:
				bot.minusVolume(volume)

		else:
			volume = int(getNumberFromString(command.args[0].name))
			if volume != None:
				bot.setVolume(volume)

def lyrics(command):
	bot.report("search them yourself faggot")

def status():
	bot.report(getStatus())

#
#playlist
#

def playlist(command):
	if len(command.args) > 0:
		if command.args[0].name in Args.Create:
			playlistCreate(command.args)
		elif command.args[0].name in Args.Delete:
			playlistDelete(command.args)
		elif command.args[0].name in Args.Add:
			playlistAdd(command.args)
		elif command.args[0].name in Args.Remove:
			playlistRemove(command.args)
		elif command.args[0].name in Args.Play:
			playlistPlay(command.args)
		elif command.args[0].name in Args.Queue:
			playlistQueue(command.args)
		elif command.args[0].name in Args.Shuffle:
			playlistShuffle(command.args)
		elif command.args[0].name in Args.Clear:
			playlistClear(command.args)
		elif command.args[0].name in Args.List:
			playlistList(command.args)
		else:
			bot.report("argument " + command.args[0].name + " not found")
	else:
		bot.report("not enough Args")

def playlistCreate(args):
	name = args[0].value
	if len(args) > 1:
		if args[1].name in Args.From:
			if args[1].value in ArgValues.Queue:
				bot.playlistCreateFromQueue(name)
			else:
				p = bot.getPlaylist(args[1].value)
				if p != None:
					bot.playlistCreateFrom(name, p)
				else:
					bot.report("couldn't find playlist")
		else:
			bot.report("specified argument not correct")
	else:
		bot.playlistCreate(name)

def playlistDelete(args):
	p = bot.getPlaylist(args[0].value)
	if p != None:
		bot.playlistDelete(p)
	else:
		bot.report("playlist not found")

def playlistAdd(args):
	if len(args) > 1:
		if args[1].name in Args.To:			
			p = bot.getPlaylist(args[1].value)
			if p != None:					
				if isURL(args[0].value):
					url = getURL(args[0].value)
					if isYoutubeURL(url):
						title = getTitleFromYoutubeURL(url)
						song = Song(url, title=title)
						bot.playlistAdd(song, p)
					else:
						bot.report("specified value is no youtube url")
				else:
					bot.report("specified value is no url")
			else:
				bot.report("playlist not found")
		else:
			bot.report("specified argument not correct")
	else:
		bot.report("not enough Args")

def playlistRemove(args):
	if len(args) > 1:
		if args[1].name in Args.From:
			p = bot.getPlaylist(args[1].value)
			if p != None:
				integer = True

				try:
					index = int(args[0].value)
				except:
					integer = False
					bot.report("enter a valid number as argument")

				if integer:
					bot.playlistRemove(index, p)
			else:
				bot.report("playlist not found")
		else:
			bot.report("specified argument not correct")
	else:
		bot.report("not enough Args")

def playlistPlay(args):
	p = bot.getPlaylist(args[0].value)
	if p != None:
		bot.playlistPlay(p)
	else:
		bot.report("playlist not found")

def playlistQueue(args):
	p = bot.getPlaylist(args[0].value)
	if p != None:
		bot.playlistQueue(p)
	else:
		bot.report("playlist not found")

def playlistShuffle(args):
	p = bot.getPlaylist(args[0].value)
	if p != None:
		bot.playlistShuffle(p)
	else:
		bot.report("playlist not found")

def playlistClear(args):
	p = bot.getPlaylist(args[0].value)
	if p != None:
		bot.playlistClear(p)
	else:
		bot.report("playlist not found")

def playlistList(args):
	if args[0].value in ArgValues.All:
		playlistListAll()
	else:
		p = bot.getPlaylist(args[0].value)
		if p != None:
			msg = playlistListPlaylist(p)
			bot.report(msg)
		else:
			bot.report("playlist not found")

def playlistListAll():
	msg = "playlists:\n"
	for p in bot.playlists:
		msg += "\n"
		msg += playlistListPlaylist(p)

	bot.report(msg)

def playlistListPlaylist(playlist):
	index = 0
	msg = playlist.name + "\n"
	for s in playlist.songs:
		msg += "(" + str(index) + ") " + s.title + " [url=" + s.url + "]URL[/url]\n"
		index += 1

	return msg