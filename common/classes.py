import os

from contextlib import contextmanager
from sys import platform


class FileSystem:

    @staticmethod
    def get_data_folder_path():
        if platform == "linux" or platform == "linux2":
            path = os.getenv("HOME")
            path += os.path.sep
            path += ".local"
            path += os.path.sep
            path += "share"
        elif platform == "darwin":
            path = os.getenv("HOME")
            path += os.path.sep
            path += "Library"
            path += os.path.sep
            path += "Preferences"
        elif platform == "win32":
            path = os.getenv("APPDATA")
        else:
            raise EnvironmentError("OS not recognizable")

        path += os.path.sep
        path += "ts3musicbot"

        return path

    @staticmethod
    def get_data_file_path():
        path = FileSystem.get_data_folder_path()
        if len(path) > 0:
            path += os.path.sep
        path += "data.json"

        return path

    @staticmethod
    def get_config_file_path():
        path = FileSystem.get_data_folder_path()
        if len(path) > 0:
            path += os.path.sep
        path += "config.json"

        return path

    @staticmethod
    def get_log_file_path():
        path = FileSystem.get_data_folder_path()
        if len(path) > 0:
            path += os.path.sep
        path += "log"

        return path


class Command:

    def __init__(self, name):
        self.name = name
        self.args = []


class Argument:

    def __init__(self, name, value=None):
        self.name = name
        self.value = value


class Playlist:

    def __init__(self, name):
        self.name = name
        self.songs = []

    def add_song(self, song):
        self.songs.append(song)

    def to_json(self):
        playlist = {
            "name": self.name,
            "songs": []
        }

        for s in self.songs:
            playlist["songs"].append(s.to_json())

        return playlist

    @staticmethod
    def json_to_playlist(json):
        playlist = Playlist(json["name"])

        for song in json["songs"]:
            playlist.add_song(Song.json_to_song(song))

        return playlist


class Song:

    def __init__(self, url, title=None):
        self.url = url
        self.title = title

    def to_json(self):
        song = {
            "url": self.url,
            "title": self.title
        }

        return song

    @staticmethod
    def json_to_song(json):
        song = Song(json["url"])
        song.title = json["title"]

        return song


class JSONData:

    @contextmanager
    def read(data, key):
        try:
            yield data[key]
        except:
            print("couldn't read " + key)
