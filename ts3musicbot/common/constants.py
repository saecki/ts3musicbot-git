class Modules:
	CLI = "c"
	WebInterface = "w"
	TerminalOnly = "t"

class JSONFields:
	Playlists = "playlists"
	SongQueue = "songQueue"
	Index = "index"
	RepeatSong = "repeatSong"

class Prefixes:
	Teamspeak = "!"

class Commands:
	Play = "play"
	PlayNext = "playnext"
	PlayNow = "playnow"
	PlayQueue = "playqueue"
	Remove = "remove"
	RemoveNext = "removenext"
	RemoveCurrent = "removecurrent"
	Pause = "pause"
	Next = "next"
	Previous = "prev"
	Stop = "stop"
	Clear = "clear"
	Shuffle = "shuffle"
	Repeat = "repeat"
	List = "list"
	Position = "position"
	Speed = "speed"
	Volume = "volume"
	Playlist = "playlist"

	Commands = {
		Play : ("play", "p"),
		PlayNext : ("playnext", "pnx"),
		PlayNow : ("playnow", "pnw"),
		PlayQueue : ("playqueue", "pq"),
		Remove : ("remove", "rm"),
		RemoveNext : ("removenext", "rn"),
		RemoveCurrent: ("removecurrent", "rc"),
		Pause : ("pause", "h"),
		Next : ("next", "n"),
		Previous : ("prev", "pr"),
		Stop : ("stop", "s"),
		Clear : ("clear", "c"),
		Shuffle : ("shuffle", "sh"),
		Repeat : ("repeat", "rp"),
		List : ("list", "ls"),
		Position : ("position", "ps"),
		Speed : ("speed", "sp"),
		Volume : ("volume", "v"),
		Playlist : ("playlist", "pl"),
		}

class Args:
	Create = "create:"
	Delete = "delete:"
	Add = "add:"
	Remove = "remove:"
	Play = "play:"
	Queue = "queue:"
	Shuffle = "shuffle:"
	Clear = "clear:"
	List = "list:"

	From = "from:"
	To = "to:"

class ArgValues:
	All = "all"
	Stop = "stop"
	Queue = "queue"

class ForbiddenNames:
	fields = [
		ArgValues.Queue,
		ArgValues.All,
		ArgValues.Stop
		]