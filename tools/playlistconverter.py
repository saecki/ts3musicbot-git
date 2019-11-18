import threading

def convertToPlaylist(string):
	names = parsePlaylistNames(string)
	print(names)

	for n in names:
		getSong(n)

def parsePlaylistNames(string):
	names = string.split("\n")
	names = [n for n in names if len(n) > 0]
	return names

def getSong(name):
	t = threading.Thread(target=cli.getYoutubeSongFromString, args=(name,))
	t.setDaemon(True)
	t.start()

p = """
Movies Alien Ant Farm
Fell On Black Days Soundgarden
Killing In The Name Rage Against The Machine
Numb Linkin Park
Here Without You 3 Doors Down
Kryptonite 3 Doors Down
Caught Up In You 38 Special
Givin the Dog a Bone AC/DC
Shake a Leg AC/DC
Rock and Roll Ain't Noise Pollution AC/DC
T.N.T. AC/DC
Highway to Hell AC/DC
Touch Too Much AC/DC
Girls Got Rhythm AC/DC
Thunderstruck AC/DC
Beat The Bastards Accept
Professoren Adam Angst
Splitter von Granaten Adam Angst
I Don't Want to Miss a Thing - From the Touchstone film, "Armageddon" Aerosmith
Walk This Way Aerosmith
Sweet Emotion Aerosmith
Breakin' Outta Hell Airbourne
School's Out Alice Cooper
Poison Alice Cooper
Smooth Criminal Alien Ant Farm
Gives You Hell The All-American Rejects
Dirty Little Secret The All-American Rejects
Rite Of Spring Angels & Airwaves
Cochise Audioslave
Show Me How to Live Audioslave
Bat Country Avenged Sevenfold
Hail to the King Avenged Sevenfold
Day Tripper - Remastered 2015 The Beatles
Yellow Submarine - Remastered 2015 The Beatles
Hey Jude - Remastered 2015 The Beatles
Let It Be - Remastered 2015 The Beatles
Come Together - Remastered 2015 The Beatles
White Wedding - Pt. 1 Billy Idol
We Didn't Start the Fire Billy Joel
Big Red Gun Billy Talent
Afraid of Heights Billy Talent
Louder Than the DJ Billy Talent
Rabbit Down the Hole Billy Talent
The Beijing Cocktail The Blackout
Bored To Death blink-182
Song 2 - 2012 Remaster Blur
Buffalo Soldier Bob Marley & The Wailers
Livin' On A Prayer Bon Jovi
It's My Life Bon Jovi
Have A Nice Day Bon Jovi
Dos Bros The BossHoss
Don't Gimme That The BossHoss
Throne Bring Me The Horizon
Tanzt du noch einmal mit mir? Broilers
Cover Me Bruce Springsteen
Born in the U.S.A. Bruce Springsteen
Surrender Cheap Trick
I Want You to Want Me Cheap Trick
Should I Stay or Should I Go - Remastered The Clash
Viva La Vida Coldplay
Zombie The Cranberries
Sunshine Of Your Love Cream
Down On The Corner Creedence Clearwater Revival
Paranoia A Day To Remember
Smoke On The Water - Remastered 2012 Deep Purple
Perfect Strangers Deep Purple
Troy Die Fantastischen Vier
Mit freundlichen Grüßen Die Fantastischen Vier
Auswärtsspiel Die Toten Hosen
Wünsch dir was Die Toten Hosen
Hier kommt Alex Die Toten Hosen
Paradies Die Toten Hosen
Alles aus Liebe Die Toten Hosen
Bonnie & Clyde Die Toten Hosen
Strom Die Toten Hosen
All die ganzen Jahre Die Toten Hosen
Kauf mich! Die Toten Hosen
Tage wie diese Die Toten Hosen
Altes Fieber Die Toten Hosen
Vogelfrei Die Toten Hosen
Wannsee Die Toten Hosen
Nichts bleibt für die Ewigkeit Die Toten Hosen
Don't Talk To Strangers Dio
Holy Diver Dio
Straight Through The Heart Dio
Rainbow In The Dark Dio
Calling Donots
Roadhouse Blues - New Stereo Mix The Doors
September Earth, Wind & Fire
Jailhouse Rock Elvis Presley
Legacy Eminem
The Monster Eminem
Survival Eminem
Let Me Be Escape the Fate
The Final Countdown Europe
Sweet Dreams (Are Made of This) - Remastered Eurythmics
Flieger, grüß mir die Sonne Extrabreit
Sturzflug Extrabreit
When I'm President Extreme
Get The Funk Out Extreme
Pornograffitti Extreme
Epic Faith No More
Centuries Fall Out Boy
Dance, Dance Fall Out Boy
Thnks fr th Mmrs Fall Out Boy
Picasso Trigger Finch
Freak Machine Fit For Rivals
Agent Orange Fit For Rivals
Damage Fit For Rivals
Slow Ride - 45 Version Foghat
Everlong Foo Fighters
The Sky Is A Neighborhood Foo Fighters
La Dee Da Foo Fighters
The Pretender Foo Fighters
Cold as Ice Foreigner
Big Time Great White
21 Guns Green Day
American Idiot Green Day
Holiday / Boulevard of Broken Dreams Green Day
Wake Me up When September Ends Green Day
Boulevard of Broken Dreams Green Day
When I Come Around Green Day
Pulling Teeth Green Day
Basket Case Green Day
Sex, Drugs & Violence Green Day
Welcome To The Jungle Guns N' Roses
Nightrain Guns N' Roses
Sweet Child O' Mine Guns N' Roses
Paradise City Guns N' Roses
Barracuda Heart
Fucked up Kids Hit The Lights
Celebrity Skin Hole
Thunder Imagine Dragons
The Wicker Man Iron Maiden
Children Of The Damned - 1998 Remastered Version Iron Maiden
Run to the Hills - 1998 Remastered Version Iron Maiden
The Trooper - 1998 Remastered Version Iron Maiden
Geile Zeit Juli
Perfekte Welle Juli
Carry on Wayward Son Kansas
Sex on Fire Kings of Leon
Use Somebody Kings of Leon
Heaven's On Fire KISS
I Was Made For Lovin' You KISS
Detroit Rock City KISS
Rock And Roll All Nite KISS
Schüsse in die Luft Kraftklub
Hand in Hand Kraftklub
Hausverbot (Chrom & Schwarz) Kraftklub
Mein Leben Kraftklub
Randale - Live Kraftklub
Fly Away Lenny Kravitz
Are You Gonna Go My Way Lenny Kravitz
A Weak Ago letlive.
Crawling Linkin Park
In the End Linkin Park
CASTLE OF GLASS Linkin Park
Sweet Home Alabama Lynyrd Skynyrd
Call Me The Breeze Lynyrd Skynyrd
Du schreibst Geschichte Madsen
Sirenen Madsen
Küss mich Madsen
Wellenreiter Massendefekt
Modern Girl Meat Loaf
I'd Do Anything For Love (But I Won't Do That) - Live From The Beacon Theatre, New York, U.S.A./1995 Meat Loaf
Nothing Else Matters Metallica
Bad Michael Jackson
They Don't Care About Us Michael Jackson
Ace of Spades Motörhead
Supermassive Black Hole Muse
Kickstart My Heart Mötley Crüe
99 Luftballons Nena
Irgendwie, irgendwo, irgendwann Nena
If Today Was Your Last Day Nickelback
How You Remind Me Nickelback
About A Girl - Remastered Nirvana
Heart-Shaped Box Nirvana
Rape Me Nirvana
The Man Who Sold The World Nirvana
Smells Like Teen Spirit Nirvana
In Bloom - Nevermind Version Nirvana
Come As You Are Nirvana
Lithium Nirvana
On A Plain Nirvana
Something In The Way Nirvana
The Kids Aren't Alright The Offspring
Pretty Fly (For A White Guy) The Offspring
Have You Ever The Offspring
Feelings The Offspring
Eye of the Tiger Survivor
Crazy Train - 2002 Version Ozzy Osbourne
What About Us P!nk
All Apologies Nirvana
So What P!nk
Funhouse P!nk
Sober P!nk
Just Like Fire (From the Original Motion Picture "Alice Through The Looking Glass") P!nk
Try P!nk
Slut Like You P!nk
Last Resort Papa Roach
Even Flow Pearl Jam
Alive Pearl Jam
Every Breath You Take - Remastered 2003 The Police
I'm Gonna Be (500 Miles) The Proclaimers
Under Pressure - Remastered 2011 Queen
Friends Will Be Friends - Remastered 2011 Queen
Who Wants To Live Forever - Remastered 2011 Queen
We Will Rock You - Remastered Queen
We Are The Champions - Remastered 2011 Queen
99 Revolutions Green Day
Spread Your Wings - Remastered 2011 Queen
Sleeping On The Sidewalk - Remastered 2011 Queen
The Way You Used to Do Queens of the Stone Age
Losing My Religion R.E.M.
Sleep Now In the Fire Rage Against The Machine
Bulls On Parade Rage Against The Machine
Testify Rage Against The Machine
Under the Bridge Red Hot Chili Peppers
Can't Stop Red Hot Chili Peppers
Get on Top Red Hot Chili Peppers
Californication Red Hot Chili Peppers
Dark Necessities Red Hot Chili Peppers
Savior Rise Against
I Don’t Want To Be Here Anymore Rise Against
The Eco-Terrorist In Me Rise Against
Satellite Rise Against
Angels Robbie Williams
Sympathy For The Devil The Rolling Stones
Gimme Shelter The Rolling Stones
"""

convertToPlaylist(p)


	

