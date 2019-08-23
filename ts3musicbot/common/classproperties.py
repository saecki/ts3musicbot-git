import os

class FileSystem:

	def getConfigFolderPath():
		path = os.path.abspath(".")
		path += os.path.sep
		path += "data"

		return path

	def getConfigFilePath():
		path = FileSystem.getConfigFolderPath()
		if len(path) > 0:
			path += os.path.sep
		path += "data.json"

		return path

	def getClientQueryFilePath():
		path = FileSystem.getConfigFolderPath()
		if len(path) > 0:
			path += os.path.sep
		path += "config.json"

		return path

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