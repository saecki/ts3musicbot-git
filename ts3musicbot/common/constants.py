class Modules:
	CLI 			= "c"
	WebInterface 	= "w"
	TerminalOnly 	= "t"

class JSONFields:
	Playlists 	= "playlists"
	SongQueue 	= "songQueue"
	Index 		= "index"
	RepeatSong 	= "repeatSong"

class Prefixes:
	Teamspeak 	= ":"

class Commands:
	Play         	= ("play", "pl")
	PlayNext 		= ("playnext", "pnx")
	PlayNow 		= ("playnow", "pnw")
	PlayQueue 		= ("playqueue", "pq")
	Remove 			= ("remove", "rm")
	RemoveNext 		= ("removenext", "rn")
	RemoveCurrent 	= ("removecurrent", "rc")
	Pause 			= ("pause", "pa")
	Next 			= ("next", "nx")
	Previous 		= ("prev", "pr")
	Stop 			= ("stop", "st")
	Clear 			= ("clear", "cl")
	Shuffle 		= ("shuffle", "sh")
	Repeat 			= ("repeat", "rp")
	List 			= ("list", "ls")
	Position 		= ("position", "ps")
	Speed 			= ("speed", "sp")
	Volume 			= ("volume", "vl")
	Playlist 		= ("playlist", "pll")

class Args:
	Create 	= ("create:", "cr:")
	Delete 	= ("delete:", "dl:")
	Add 	= ("add:", "ad:")
	Remove 	= ("remove:", "rm:")
	Play 	= ("play:", "pl:")
	Queue 	= ("queue:", "qu:")
	Shuffle = ("shuffle:", "sh:")
	Clear 	= ("clear:", "cl:")
	List 	= ("list:", "ls:")

	From 	= ("from:", "fr:")
	To 		= ("to:")

class ArgValues:
	All 	= ("all", "a")
	Stop 	= ("stop", "s")
	Queue 	= ("queue", "q")

class ForbiddenNames:
	fields = (
		ArgValues.Queue,
		ArgValues.All,
		ArgValues.Stop,
		)