import pafy
import vlc
import os
import asyncio
import time

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

def playAudioFromUrl(url):
	
	video = pafy.new(url)
	best = video.getbest()
	playurl = best.url
	
	Media = Instance.media_new(playurl)
	Media.get_mrl()
	player.set_media(Media)
	player.play()

def handleCommand(command):
	if "!play" in command:
		tempurl = command
		tempurl = tempurl.replace("[URL]", "") 
		tempurl = tempurl.replace("[/URL]", "")
		l = tempurl.split("!play ", 1)
		if len(l) > 1:
			url = l[1]
			playAudioFromUrl(url)
			print("playing: " + url)
		else:
			player.play()
			print("resumed")	
	elif "!pause" in command:
		player.pause()
		print("paused")
	elif "!stop" in command:
		player.stop()
		print("stopped")
	else:
		print("The command: " + command + "has a wrong syntax")

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

		if player.get_state() == vlc.State.Ended:
			player.stop()
			print("song ended")

		await asyncio.sleep(0.5)

print("Waiting for a command")

lastLine = getFileLineCount(getTS3ChannelChatFilePath())

loop = asyncio.get_event_loop()
loop.create_task(mainLoop())

try:
	loop.run_forever()
except KeyboardInterrupt:
	pass
finally:
	loop.run_until_complete(loop.shutdown_asyncgens())
	loop.close()

print("Exiting")
