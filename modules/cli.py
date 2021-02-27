import re
import sys
import urllib.request
import vlc

from bs4 import BeautifulSoup

import ts3musicbot as bot

from common.classes import Argument, FileSystem, Song, Command
from common.constants import Args, ArgValues, Commands


def run():
    print("starting cli")
    bot.add_thread(target=start_checking_for_terminal_command, daemon=True)
    print("started cli")


def update():
    pass


def report(string):
    print(string)


#
# terminal
#

def start_checking_for_terminal_command():
    if bot.silent:
        sys.stdout = open(FileSystem.get_log_file_path(), "a")
        sys.stderr = open(FileSystem.get_log_file_path(), "a")

    while bot.running:
        string = input()
        command = parse_command(string)
        with bot.lock:
            handle_command(command)


#
# commands
#

def handle_command(command, prefix=("",)):
    if command is not None:
        startswithprefix = None
        for p in prefix:
            if command.name.startswith(p):
                startswithprefix = p
                break

        if startswithprefix == "":
            if command.name in Commands.Exit:
                bot.quit()

        if startswithprefix is not None:
            command.name = command.name[len(startswithprefix):]
            if command.name in Commands.Play:
                play(command)
            elif command.name in Commands.PlayNext:
                play_next(command)
            elif command.name in Commands.PlayNow:
                play_now(command)
            elif command.name in Commands.PlayQueue:
                play_queue(command)
            elif command.name in Commands.Remove:
                remove(command)
            elif command.name in Commands.RemoveNext:
                remove_next()
            elif command.name in Commands.RemoveCurrent:
                remove_current()
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
                list(command)
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
            elif command.name in Commands.Help:
                help()
            else:
                bot.report("the command: " + command.name + " wasn't found")
    else:
        bot.report("wow that's impressive")


def parse_command(string):
    if type(string) == str:
        string = string.rstrip()
        string = stripURL(string)
        fields = string.split(" ")

        if len(fields) > 0:
            commandName = fields[0].lower()
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
# convenient
#

def get_number_from_string(string):
    try:
        num = float(string)
    except:
        return None
    return num


def stripURL(string):
    string = string.replace("[url]", "")
    string = string.replace("[/url]", "")
    string = string.replace("[URL]", "")
    string = string.replace("[/URL]", "")
    return string


#
# url
#

def is_youtube_url(url):
    if "https://youtu.be/" in url or "https://www.youtube.com/watch?v=" in url:
        return True
    else:
        return False


def get_command_args_as_string(args, start=0, startWithArgVal=False, end=None, till=()):
    length = len(args)

    if startWithArgVal:
        if start < length:
            msg = args[start].value
        start += 1
    else:
        msg = ""

    if end == None:
        end = length

    if length > start and length >= end:
        for i in range(start, end):
            n = args[i].name
            if n in till:
                break
            else:
                msg += n + " "

            v = args[i].value
            if v is not None:
                if v in till:
                    break
                else:
                    msg += v + " "
    return msg


def get_youtube_song_from_string(string):
    try:
        query = urllib.parse.quote(string)
        url = "https://www.youtube.com/results?search_query=" + query
        response = urllib.request.urlopen(url).read()
        html = response.decode("utf-8")

        pattern = re.compile("\{\"videoRenderer\":\{\"videoId\":\"(.*?)\",(.*?)\"title\":\{\"runs\":\[{\"text\":\"(.*?)\"\}\],")
        matches = re.findall(pattern, html)

        video_id = matches[0][0]
        url = "https://www.youtube.com/watch?v=" + video_id
        title = matches[0][2].replace("\\", "")

        return Song(url, title=title)
    except Exception as e:
        bot.report("couldn't find youtube song")

    return None


def get_title_from_youtube_url(url):
    try:
        response = urllib.request.urlopen(url)
        html = response.read()
        soup = BeautifulSoup(html, "html.parser")
        meta = soup.find(attrs={"name": "title"})
        title = meta.get("content")
        return title
    except:
        bot.report("couldn't get title from youtube url")

    return None


def get_youtube_song_from_play_command(command):
    url = command.args[0].name
    if is_youtube_url(url):
        title = get_title_from_youtube_url(url)
        if title is not None:
            song = Song(url, title=title)
            return song
        else:
            bot.report("couldn't find the song")
    else:
        string = get_command_args_as_string(command.args)
        song = get_youtube_song_from_string(string)

        if song is not None:
            return song
        else:
            bot.report("couldn't find any youtube song")

    return None


def get_youtube_song_from_playlist_command(args, tillArg=None):
    string = get_command_args_as_string(args, startWithArgVal=True, till=tillArg)
    url = args[0].value
    if is_youtube_url(url):
        title = get_title_from_youtube_url(url)
        song = Song(url, title=title)
        return song
    elif args[0].value in ArgValues.CurrentSong:
        return bot.get_current_song()
    elif get_number_from_string(string) is not None:
        return bot.get_song(int(get_number_from_string(args[0].value)))
    else:
        song = None
        for a in tillArg:
            if a in [a.name for a in args]:
                song = get_youtube_song_from_string(string)
                break

        if song is not None:
            return song
        else:
            bot.report("couldn't find any youtube song")

    bot.report("well ... respect")
    return None


#
# strings
#

def get_status():
    msg = "status:\n"
    msg += "playback state: " + str(bot.player.get_state()) + "\n"
    if get_current_song_title() is not None:
        msg += "title: " + get_current_song_title() + "\n"
        msg += "position: " + get_position() + "\n"
    msg += "speed: " + get_speed() + "\n"
    msg += "volume: " + get_volume() + "\n"
    msg += "repeat: " + get_repeat() + "\n"
    msg += "index: " + str(bot.index) + "\n"
    msg += "songQueue length: " + str(len(bot.songQueue)) + "\n"
    return msg


def get_playback_info():
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
            msg += " | " + get_position()
    return msg


def get_current_song_title():
    song = bot.get_current_song()
    if song is not None:
        return song.title
    return None


def get_position():
    return str(round(bot.player.get_position() * 100)) + "%"


def get_speed():
    return str(round(bot.player.get_rate() * 100)) + "%"


def get_volume():
    return str(bot.player.audio_get_volume()) + "%"


def get_repeat():
    if bot.repeatSong == 0:
        return "none"
    elif bot.repeatSong == 1:
        return "song"
    else:
        return "all"


#
# queue
#

def play(command):
    if len(command.args) > 0:
        song = get_youtube_song_from_play_command(command)
        if song is not None:
            bot.play(song)
    else:
        bot.play()


def play_next(command):
    if len(command.args) > 0:
        song = get_youtube_song_from_play_command(command)
        if song is not None:
            bot.play_next(song)
    else:
        bot.report("not enough Args")


def play_now(command):
    if len(command.args) > 0:
        song = get_youtube_song_from_play_command(command)
        if song is not None:
            bot.play_now(song)
    else:
        bot.report("not enough Args")


def play_queue(command):
    if len(command.args) > 0:
        integer = True

        try:
            index = int(command.args[0].name)
        except:
            integer = False
            bot.report("enter a valid number as argument")

        if integer:
            bot.play_queue(index)


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


def remove_next():
    bot.remove_next()


def remove_current():
    bot.remove_current()


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


def list(command):
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

    if len(command.args) > 0 and command.args[0].name in ArgValues.All:
        playlist_list_all()


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
            position = get_number_from_string(string)

            if position is not None:
                bot.plus_position(position)

        elif command.args[0].name.startswith("-"):
            string = command.args[0].name[1:]
            position = get_number_from_string(string)

            if position is not None:
                bot.minus_position(position)

        else:
            position = get_number_from_string(command.args[0].name)
            if position is not None:
                bot.set_position(position)


def speed(command):
    if len(command.args) > 0:
        if command.args[0].name.startswith("+"):
            string = command.args[0].name[1:]
            speed = get_number_from_string(string)

            if speed is not None:
                bot.plus_speed(speed)

        elif command.args[0].name.startswith("-"):
            string = command.args[0].name[1:]
            speed = get_number_from_string(string)

            if speed is not None:
                bot.minus_speed(speed)

        else:
            speed = get_number_from_string(command.args[0].name)
            if speed is not None:
                bot.set_speed(speed)


def volume(command):
    if len(command.args) > 0:
        if command.args[0].name.startswith("+"):
            string = command.args[0].name[1:]
            volume = get_number_from_string(string)
            if volume is not None:
                bot.plus_volume(int(volume))
                return

        elif command.args[0].name.startswith("-"):
            string = command.args[0].name[1:]
            volume = get_number_from_string(string)
            if volume is not None:
                bot.minus_volume(int(volume))
                return

        else:
            volume = get_number_from_string(command.args[0].name)
            if volume is not None:
                bot.set_volume(int(volume))
                return
    bot.report("specified arguments not correct or missing")


def lyrics(command):
    bot.report("search them yourself faggot")


def status():
    bot.report(get_status())


#
# playlist
#

def playlist(command):
    if len(command.args) > 0:
        if command.args[0].name in Args.Create:
            playlist_create(command.args)
        elif command.args[0].name in Args.Delete:
            playlist_delete(command.args)
        elif command.args[0].name in Args.Add:
            playlist_add(command.args)
        elif command.args[0].name in Args.Remove:
            playlist_remove(command.args)
        elif command.args[0].name in Args.Play:
            playlist_play(command.args)
        elif command.args[0].name in Args.Queue:
            playlist_queue(command.args)
        elif command.args[0].name in Args.Shuffle:
            playlist_shuffle(command.args)
        elif command.args[0].name in Args.Clear:
            playlist_clear(command.args)
        elif command.args[0].name in Args.List:
            playlist_list(command.args)
        else:
            bot.report("argument " + command.args[0].name + " not found")
    else:
        bot.report("not enough Args")


def playlist_create(args):
    name = args[0].value
    if len(args) > 1:
        if args[1].name in Args.From:
            if args[1].value in ArgValues.Queue:
                bot.playlist_create_from_queue(name)
            else:
                p = bot.get_playlist(args[1].value)
                if p is not None:
                    bot.playlist_create_from(name, p)
                else:
                    bot.report("couldn't find playlist")
        else:
            bot.report("specified arguments not correct or missing")
    else:
        bot.playlist_create(name)


def playlist_delete(args):
    p = bot.get_playlist(args[0].value)
    if p is not None:
        bot.playlist_delete(p)
    else:
        bot.report("playlist not found")


def playlist_add(args):
    if len(args) > 1:
        toArg = None
        for a in args:
            if a.name in Args.To:
                toArg = a
                break

        if toArg is not None and toArg.value is not None:
            p = bot.get_playlist(toArg.value)
            if p is not None:
                _playlist_add(p, args)
            else:
                bot.report("playlist not found")
        else:
            bot.report("specified arguments not correct or missing")
    else:
        bot.report("not enough Args")


def _playlist_add(playlist, args):
    name = args[0].value
    if name in ArgValues.Queue:
        bot.playlist_add_queue(playlist)
        return

    addedPlaylist = None
    for p in bot.playlists:
        if name == p.name:
            addedPlaylist = p
            break
    if addedPlaylist is not None:
        bot.playlist_add_playlist(addedPlaylist, playlist)
        return

    song = get_youtube_song_from_playlist_command(args, tillArg=Args.To)
    if song is not None:
        bot.playlist_add(song, playlist)


def playlist_remove(args):
    if len(args) > 1:
        if args[1].name in Args.From:
            p = bot.get_playlist(args[1].value)
            if p is not None:
                integer = True

                try:
                    index = int(args[0].value)
                except:
                    integer = False
                    bot.report("enter a valid number as argument")

                if integer:
                    bot.playlist_remove(index, p)
            else:
                bot.report("playlist not found")
        else:
            bot.report("specified arguments not correct or missing")
    else:
        bot.report("not enough Args")


def playlist_play(args):
    p = bot.get_playlist(args[0].value)
    if p is not None:
        bot.playlist_play(p)
    else:
        bot.report("playlist not found")


def playlist_queue(args):
    p = bot.get_playlist(args[0].value)
    if p is not None:
        bot.playlist_queue(p)
    else:
        bot.report("playlist not found")


def playlist_shuffle(args):
    p = bot.get_playlist(args[0].value)
    if p is not None:
        bot.playlist_shuffle(p)
    else:
        bot.report("playlist not found")


def playlist_clear(args):
    p = bot.get_playlist(args[0].value)
    if p is not None:
        bot.playlist_clear(p)
    else:
        bot.report("playlist not found")


def playlist_list(args):
    if args[0].value in ArgValues.All:
        playlist_list_all()
    else:
        p = bot.get_playlist(args[0].value)
        if p is not None:
            msg = playlist_list_playlist(p)
            bot.report(msg)
        else:
            bot.report("playlist not found")


def playlist_list_all():
    msg = "playlists:\n"
    for p in bot.playlists:
        msg += "\n"
        msg += playlist_list_playlist(p)
    bot.report(msg)


def playlist_list_playlist(playlist):
    index = 0
    msg = playlist.name + "\n"
    for s in playlist.songs:
        msg += "(" + str(index) + ") " + s.title + " [url=" + s.url + "]URL[/url]\n"
        index += 1
    return msg


def help():
    bot.report("help me")
