import json
import os
import sys
import pafy
import random
import threading
import time
import vlc

from common.classes import Playlist, FileSystem, Song, JSONData
from common.constants import ForbiddenNames, JSONFields, Modules
from modules import cli, teamspeak, zmqserver

modules = []
threads = []
lock = None
clientQueryLock = None
running = True
debug = False
silent = False

Instance = None
player = None

playlists = []
songQueue = []
index = 0
repeatSong = 0

last_line = None


def run(args=Modules.TeamSpeak + Modules.CLI):
    global lock
    global clientQueryLock
    global debug
    global silent

    if Modules.SILENT in args:
        silent = True
        sys.stdout = open(FileSystem.get_log_file_path(), "a")
        sys.stderr = open(FileSystem.get_log_file_path(), "a")

    print("####################\nstarting...")

    if not create_vlc_player():
        print("error while connecting to vlc exiting")
        exit()

    read_data()

    lock = threading.Lock()
    clientQueryLock = threading.Lock()

    main_thread = add_thread(target=main_loop)
    add_thread(target=frequently_write_data, daemon=True)

    if Modules.CLI in args:
        modules.append(cli)

    if Modules.TeamSpeak in args:
        modules.append(teamspeak)

    if Modules.ZMQ in args:
        modules.append(zmqserver)

    if Modules.Debug in args:
        print("running in debug mode")
        debug = True

    for m in modules:
        m.run()

    start_threads()

    report("ready")


def quit():
    global running

    report("exiting")
    write_data()
    running = False
    exit()


def start_new_thread(target=None, args=None, daemon=False):
    t = create_thread(target=target, args=args, daemon=daemon)
    if t is not None:
        t.start()
    return t


def add_thread(target=None, args=None, daemon=False):
    t = create_thread(target=target, args=args, daemon=daemon)
    if t is not None:
        threads.append(t)
    return t


def create_thread(target=None, args=None, daemon=False):
    if target is not None:
        t = None
        if args == None:
            t = threading.Thread(target=target)
        else:
            t = threading.Thread(target=target, args=args)
        t.setDaemon(daemon)
        return t
    return None


def start_threads():
    for t in threads:
        t.start()


def main_loop():
    global last_line
    global index

    while running:
        for m in modules:
            m.update()

        if player.get_state() == vlc.State.Ended:
            if repeatSong == 0:
                next()
            elif repeatSong == 1:
                play_song()
            elif repeatSong == 2:
                if index >= len(songQueue) - 1:
                    index = 0
                    play_song()
                else:
                    next()
        time.sleep(0.5)


def frequently_write_data():
    while running:
        with lock:
            write_data()
        time.sleep(600)


def report(string):
    for m in modules:
        m.report(string)


#
# convenient
#

def get_number_between(number, min, max):
    if number < min:
        return min
    elif number > max:
        return max
    else:
        return number


#
# file system
#

def write_data():
    data = {
        JSONFields.Playlists: [],
        JSONFields.SongQueue: [],
        JSONFields.Index: index,
        JSONFields.RepeatSong: repeatSong
    }

    for p in playlists:
        data[JSONFields.Playlists].append(p.to_json())

    for s in songQueue:
        data[JSONFields.SongQueue].append(s.to_json())

    try:
        with open(FileSystem.get_data_file_path(), "w") as jsonfile:
            json.dump(data, jsonfile, indent=4)
    except:
        print("couldn't write data")


def read_data():
    global playlists
    global index
    global repeatSong

    try:
        with open(FileSystem.get_data_file_path()) as json_file:
            data = json.load(json_file)

            with JSONData.read(data, JSONFields.Playlists) as json_playlists:
                for p in json_playlists:
                    playlists.append(Playlist.json_to_playlist(p))

            with JSONData.read(data, JSONFields.SongQueue) as json_song_queue:
                for s in json_song_queue:
                    songQueue.append(Song.json_to_song(s))

            with JSONData.read(data, JSONFields.Index) as json_field:
                index = json_field
                if json_field >= len(songQueue) and json_field != 0:
                    index = len(songQueue) - 1

            with JSONData.read(data, JSONFields.RepeatSong) as json_field:
                repeatSong = json_field

        return True
    except:
        report("couldn't read config file")
        report("trying to create the conifg folder")
        try:
            os.mkdir(FileSystem.get_data_folder_path())
        except FileExistsError:
            report("config folder existed")
    return False


#
# getters
#

def get_song(index):
    length = len(songQueue)
    if length > 0:
        i = get_number_between(index, 0, length - 1)
        return songQueue[i]
    return None


def get_current_song():
    if is_playing_or_paused() and index < len(songQueue):
        return songQueue[index]
    else:
        return None


#
# url
#

def get_best_youtube_audio_url(url):
    video = pafy.new(url)
    best = video.getbestaudio()
    play_url = best.url
    return play_url


#
# playback
#

def create_vlc_player():
    global Instance
    global player

    for i in range(0, 5):
        try:
            Instance = vlc.Instance()
            player = Instance.media_player_new()
            return True
        except:
            report("couldn't create vlc player in the " + str(i + 1) + ". try")
    return False


def play_song():
    if index < len(songQueue):
        song = songQueue[index]
        start_new_thread(target=play_audio_from_song, args=(song,), daemon=True)
    else:
        report("there is nothing to play")


def play_audio_from_song(song):
    try:
        play_url = get_best_youtube_audio_url(song.url)

        media = Instance.media_new(play_url)
        media.get_mrl()
        player.set_media(media)
        player.play()
        report("playing " + song.title + " [url=" + song.url + "]URL[/url]")
    except:
        create_vlc_player()
        report("couldn't play song " + song.title + " [url=" + song.url + "]URL[/url]")


def is_playing_or_paused():
    if player.get_state() == vlc.State.Playing or player.get_state() == vlc.State.Paused:
        return True
    return False


def set_position(position):
    position = get_number_between(position, 0, 100)
    position = position / 100

    try:
        for i in range(0, 5):
            if player.set_position(
                    position) is None:  # Should be checking for 0 but this library is shit and returns None
                time.sleep(0.1)
                report("set position to " + str(round(player.get_position() * 100)) + "%")
                return
    except:
        pass
    report("couldn't update position")


def plus_position(position):
    set_position(player.get_position() * 100 + position)


def minus_position(position):
    set_position(player.get_position() * 100 - position)


def set_speed(speed):
    rate = get_number_between(speed, 25, 400)
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


def plus_speed(speed):
    set_speed(player.get_rate() * 100 + speed)


def minus_speed(speed):
    set_speed(player.get_rate() * 100 - speed)


def set_volume(volume):
    try:
        for i in range(0, 5):
            if player.audio_set_volume(get_number_between(volume, 0, 130)) == 0:
                time.sleep(0.1)
                report("set volume to " + str(player.audio_get_volume()))
                return
    except:
        pass
    report("couldn't update volume")


def plus_volume(volume):
    set_volume(player.audio_get_volume() + volume)


def minus_volume(volume):
    set_volume(player.audio_get_volume() - volume)


#
# queue
#

def play(song=None):
    if song == None:
        if player.get_state() == vlc.State.Paused:
            player.play()
            report("resumed")
        elif player.get_state() != vlc.State.Playing:
            play_song()
        else:
            report("already playing")
    else:
        songQueue.append(song)
        report("added " + song.title + " [url=" + song.url + "]URL[/url] to the queue")

        if len(songQueue) == 1:
            play_song()
        elif not (is_playing_or_paused()):
            next()


def play_next(song):
    songQueue.insert(index + 1, song)
    report("added " + song.title + " [url=" + song.url + "]URL[/url] as next song to the queue")


def play_now(song):
    songQueue.insert(index + 1, song)
    if len(songQueue) == 1:
        play_song()
    else:
        next()


def play_queue(i):
    global index

    index = get_number_between(i, 0, len(songQueue) - 1)
    play_song()


def remove(i):
    global index

    if len(songQueue) > 0:
        i = get_number_between(i, 0, len(songQueue) - 1)

        if i == index:
            remove_current()
        else:
            title = songQueue[i].title

            del songQueue[i]
            if i < index:
                index -= 1
            report("removed song " + title + " at index " + str(i) + " from the queue")
    else:
        report("no songs to remove")


def remove_next():
    if index < len(songQueue) - 1:
        title = songQueue[index + 1].title

        del songQueue[index + 1]
        report("removed next song " + title + " from the queue")
    else:
        report("already playing last song")


def remove_current():
    global index

    if len(songQueue) > 0:
        title = songQueue[index].title

        del songQueue[index]
        report("removed current song " + title + " from the queue")
        if index >= len(songQueue) and index != 0:
            index = len(songQueue) - 1
            if is_playing_or_paused():
                stop()
        elif is_playing_or_paused():
            play_song()
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
        play_song()
    elif repeatSong == 2:
        index = len(songQueue) - 1
        report("previous song")
        play_song()
    else:
        report("already playing first song")


def next():
    global index

    player.stop()
    if index < len(songQueue) - 1:
        index += 1
        report("next song")
        play_song()
    elif repeatSong == 2:
        index = 0
        report("next song")
        play_song()
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
    fixed_song = songQueue[index]
    fixed_index = index

    random.shuffle(songQueue)

    new_index = songQueue.index(fixed_song)
    songQueue[fixed_index], songQueue[new_index] = songQueue[new_index], songQueue[fixed_index]

    report("shuffled queue")


def repeat(mode):
    global repeatSong

    repeatSong = get_number_between(mode, 0, 2)

    if repeatSong == 0:
        report("stopped repeating")
    elif repeatSong == 1:
        report("repeating one song")
    else:
        report("repeating all songs")


#
# playlist
#

def get_playlist(name):
    for p in playlists:
        if p.name == name:
            return p
    return None


def playlist_create(name):
    if not is_forbidden(name):
        p = Playlist(name)
        playlists.append(p)
        report("created " + name)


def playlist_create_from_queue(name):
    if not is_forbidden(name):
        p = Playlist(name)
        p.songs = songQueue.copy()
        playlists.append(p)
        report("created " + name + " from the queue")


def playlist_create_from(name, playlist):
    if not is_forbidden(name):
        p = Playlist(name)
        p.songs = playlist.songs.copy()
        playlists.append(p)
        report("created " + name + " from " + playlist.name)


def is_forbidden(name):
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


def playlist_delete(playlist):
    playlists.remove(playlist)
    report("deleted " + playlist.name)


def playlist_add(song, playlist):
    playlist.add_song(song)
    report("added " + song.title + " to " + playlist.name)


def playlist_add_playlist(addedPlaylist, playlist):
    for s in addedPlaylist.songs:
        playlist.add_song(s)
    report("added " + addedPlaylist.name + " to " + playlist.name)


def playlist_add_queue(playlist):
    for s in songQueue:
        playlist.add_song(s)
    report("added the queue to " + playlist.name)


def playlist_remove(index, playlist):
    index = get_number_between(index, 0, len(songQueue) - 1)
    title = playlist.songs[index].title
    del playlist.songs[index]
    report("removed song " + title + " at index " + str(index) + " from " + playlist.name)


def playlist_play(playlist):
    global songQueue
    global index

    songQueue = playlist.songs.copy()
    index = 0
    report("replaced the queue with " + playlist.name)
    play_song()


def playlist_queue(playlist):
    global songQueue

    songQueue = songQueue + playlist.songs
    report("added songs from " + playlist.name + " to the queue")
    if player.get_state() != vlc.State.Playing or player.get_state() == vlc.State.Paused:
        play_song()


def playlist_shuffle(playlist):
    random.shuffle(playlist.songs)
    report("shuffled " + playlist.name)


def playlist_clear(playlist):
    playlist.songs.clear()
    report("cleared " + playlist.name)
