import os
from abc import ABC, abstractmethod

class FileSystem:

	def getConfigFolderPath():
		path = os.getenv("APPDATA")
		path += os.path.sep
		path += "TS3MusicBot"

		return path

	def getConfigFilePath():
		path = FileSystem.getConfigFolderPath()
		if len(path) > 0:
			path += os.path.sep
		path += "config.json"

		return path

	def getClientQueryFilePath():
		path = FileSystem.getConfigFolderPath()
		if len(path) > 0:
			path += os.path.sep
		path += "ts3clientquery.json"

		return path

	def getTS3ChannelChatFilePath():
		p = os.getenv("APPDATA")
		p += os.path.sep
		p += "TS3Client\\chats"

		all_subdirs = FileSystem.getAllSubdirsOf(p)
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

	def getLineCountOf(path):
		try:
			return sum(1 for line in open(path))
		except:
			pass
		return 0


class TS3MusicBotModule:

	def __init__(ABC):
		pass

	@abstractmethod
	def update(self):
		pass

	@abstractmethod
	async def report(self, string):
		pass

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
		self.songs = []

	def addSong(self, song):
		self.songs.append(song)

	def toJSON(self):
		playlist = {}
		playlist["name"] = self.name
		playlist["songs"] = []
		for s in self.songs:
			playlist["songs"].append(s.toJSON())

		return playlist

	def jsonToPlaylist(json):
		playlist = Playlist(json["name"])
		for song in json["songs"]:
			playlist.addSong(Song.jsonToSong(song))

		return playlist

class Song:

	def __init__(self, url, title=None):
		self.url = url
		self.title = title

	def toJSON(self):
		song = {}
		song["url"] = self.url
		song["title"] = self.title

		return song

	def jsonToSong(json):
		song = Song(json["url"])
		song.title = json["title"]

		return song