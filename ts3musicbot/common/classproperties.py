from abc import ABC, abstractmethod

class TS3MusicBotModule:

	def __init__(ABC):
		pass

	@abstractmethod
	def update(self):
		pass

	@abstractmethod
	def report(self, string):
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