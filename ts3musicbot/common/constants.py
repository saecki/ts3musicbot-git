class Modules:
	CLI = "c"
	WebInterface = "w"

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
	Volume = "volume"
	Playlist = "playlist"

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