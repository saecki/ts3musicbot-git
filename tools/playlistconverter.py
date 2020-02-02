import threading
import sys

IN_FILE = "if="
OUT_FILE = "of="


def convert_to_playlist(string):
    names = parse_playlist_names(string)
    print(names)

    for n in names:
        get_song(n)


def parse_playlist_names(string):
    names = string.split("\n")
    names = [n for n in names if len(n) > 0]
    return names


def get_song(name):
    t = threading.Thread(target=parse_playlist_names)  # modules.cli.get_youtube_song_from_string, args=(name,))
    t.setDaemon(True)
    t.start()


if __name__ == '__main__':
    args = sys.argv[1:]

    for a in args:
        print(a)

    if args[0].startswith(IN_FILE):

        path = args[0].replace(IN_FILE, "")

        with open(path, "r") as in_file:
            for line in in_file:
                print(line)