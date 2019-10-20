# ts3musicbot
A musicbot for Teamspeak which uses VLC to directly stream audio from YouTube.


## Table of Content
- [Command Line Interface](#command-line-interface)
  - [Usage](#usage)
  - [Syntax](#syntax)
  - [Prefixes](#prefixes)
  - [Commands](#commands)
  - [Short Forms](#short-forms)
  - [Examples](#examples)
    - [Teamspeak](#teamspeak)
    - [Terminal](#terminal)
- [Dependencies](#dependencies)
- [Setup](#setup)

## Command Line Interface

### Usage
To control the bot on teamspeak send a command to the channel the bot is currently inside. 

### Syntax
Commands are built upon a structure.
A command starts with a keyword and can be followed up by certain arguments seperated with spaces which further specify the behavior of the command.  
Arguments on their own can require values, if so they will end with a colon and the values need to be specified behind seperated by spaces aswell.  
Depending on the platform commands can have prefixes to which the command keywords are simply appended.  

An example command written on teamspeak could look like this:  
```!command arg1: value1 arg2 arg3: value3```

### Prefixes
| Plattform | Prefix |
| ---       | --- |
| Teamspeak | ! or : |
| Terminal  | ```None``` |

### Commands 
| Function                                                    | Command |
| ---                                                         | --- |
| adding a song to the queue                                  | ```Prefix```play ```song*``` |
| playing a song right after the current song                 | ```Prefix```playnext ```song*``` |
| playing a song right now                                    | ```Prefix```playnow ```song*``` |
| playing a song at a certain index in the queue              | ```Prefix```playqueue ```index``` |
| resuming the song                                           | ```Prefix```play |
| removing the song at a certain index                        | ```Prefix```remove ```index``` |
| removing the next song                                      | ```Prefix```removenext |
| removing the current song                                   | ```Prefix```removecurrent |
| pausing the song                                            | ```Prefix```pause |
| toggling the playback state                                 | ```Prefix```toggle |
| playing the next song                                       | ```Prefix```next |
| playing the previous song                                   | ```Prefix```prev |
| stopping the song                                           | ```Prefix```stop |
| clearing the queue                                          | ```Prefix```clear |
| repeating one song                                          | ```Prefix```repeat |
| repeating all songs                                         | ```Prefix```repeat all |
| stop repeating                                              | ```Prefix```repeat stop |
| shuffling the queue                                         | ```Prefix```shuffle |
| listing the queue                                           | ```Prefix```list |
| setting the playback position in percent                    | ```Prefix```position ```value```|
| adding a value to the position                              | ```Prefix```position ```+value```|
| subtracting a value from the position                       | ```Prefix```position ```-value```|
| setting the playback speed in percent                       | ```Prefix```speed ```value```|
| adding a value to the speed                                 | ```Prefix```speed ```+value```|
| subtracting a value from the speed                          | ```Prefix```speed ```-value```|
| setting the volume to a value between 0 to 120              | ```Prefix```volume ```value```|
| adding a value to the volume                                | ```Prefix```volume ```+value```|
| subtracting a value from the volume                         | ```Prefix```volume ```-value```|
|                                                             |
| creating a playlist                                         | ```Prefix```playlist create: ```name``` |
| creating a playlist from the queue                          | ```Prefix```playlist create: ```name``` from: queue |
| creating a playlist from another playlist                   | ```Prefix```playlist create: ```name``` from: ```playlist``` |
| deleteting a playlist                                       | ```Prefix```playlist delete: ```name``` |
| adding a song to a playlist                                 | ```Prefix```playlist add: ```song*``` to: ```name``` |
| adding a song at a certain index of the queue to a playlist | ```Prefix```playlist add: ```index``` to: ```name``` |
| adding the current song to a playlist                       | ```Prefix```playlist add: currentsong to: ```name``` |
| adding the queue to a playlist                              | ```Prefix```playlist add: queue to: ```name``` |
| adding a playlist to another playlist                       | ```Prefix```playlist add: ```playlist``` to: ```name``` |
| removing a song at a certain index from a playlist          | ```Prefix```playlist remove: ```index``` from: ```name``` |
| adding the playlist to the queue                            | ```Prefix```playlist queue: ```name``` |
| replacing the queue with a playlist                         | ```Prefix```playlist play: ```name``` |
| shuffling a playlist                                        | ```Prefix```playlist shuffle: ```name``` |
| clearing a playlist                                         | ```Prefix```playlist clear: ```name``` |
| listing all playlists                                       | ```Prefix```playlist list: all |
| listing a playlist                                          | ```Prefix```playlist list: ```name``` |
|                                                             |
| make the bot join your channel                              | ```Prefix```comeover |
\* songs can be youtube urls or just text which will be used to search a song on youtube

### Short Forms
| Command       | Short Form |
| ---           | --- |
| play          | pl |
| playnext      | pnx |
| playnow       | pnw |
| playqueue     | pq |
| remove        | rm |
| removenext    | rn |
| removecurrent | rc |
| pause         | pa |
| toggle        | tg |
| next          | nx |
| prev          | pr |
| stop          | st |
| clear         | cl |
| shuffle       | sh |
| repeat        | rp |
| list          | ls |
| position      | ps |
| speed         | sp |
| volume        | vl |
| playlist      | pll |
| comeover      | co |

| Argument | Short Form |
| ---      | --- |
| create:  | cr: |
| delete:  | dl: |
| add:     | ad: |
| remove:  | rm: |
| play:    | pl: |
| queue:   | qu: |
| shuffle: | sh: |
| clear:   | cl: |
| list:    | ls: |
| from:    | fr: |

| Argument Values | Short Form |
| ---             | --- |
| all             | a |
| stop            | s |
| queue           | q |
| currentsong     | cs |

### Examples

#### Teamspeak
- **Play Owl City - Fireflies from YouTube:**  
  
  by the automatic search function  
  ```!play owl city fireflies```  
  
  by directly providing a YouTube URL  
  ```!play https://www.youtube.com/watch?v=psuRGfAaju4```  

- **Create a playlist named myplaylist:**  

  ```!playlist create: myplaylist```  

- **Add a song to the playlist myplaylist:**  

  ```!playlist add: https://www.youtube.com/watch?v=psuRGfAaju4 to: myplaylist```  

- **Queue the playlist myplaylist:**  

  ```!playlist queue: myplaylist```  

#### Terminal

- **Play Owl City - Fireflies from YouTube:**  
  
  by the automatic search function  
  ```play owl city fireflies```  
  
  by directly providing a YouTube URL  
  ```play https://www.youtube.com/watch?v=psuRGfAaju4```  

- **Create a playlist named myplaylist:**  

  ```playlist create: myplaylist```  

- **Add a song to the playlist myplaylist:**  

  ```playlist add: https://www.youtube.com/watch?v=psuRGfAaju4 to: myplaylist```  

- **Queue the playlist myplaylist:**  

  ```playlist queue: myplaylist```  

## Dependencies
- [Python 3.7](https://www.python.org/downloads/)
   - [requirements.txt](https://github.com/Saecki/ts3musicbot-git/blob/master/ts3musicbot/requirements.txt)
- [TeamSpeak 3 client](https://www.teamspeak.com/en/downloads/)
   - [ClientQuery plugin](https://www.myteamspeak.com/addons/943dd816-7ef2-48d7-82b8-d60c3b9b10b3)
- [VLC media player 3.0](https://www.videolan.org/vlc/)
- [VB-CABLE](https://www.vb-audio.com/Cable/) (or another app for routing audio as an input to teamspeak)

## Setup
- Clone or download ts3musicbot-git
- Download and install Python, TeamSpeak, VLC media player and VB-CABLE
- Navigate into the ts3musicbot-git/ts3musicbot directory that you've downloaded and install all python dependencies by executing the command: ```pip3 install -r requirements.txt```.
- Install the ClientQuery plugin in TeamSpeak directly by going to: Tools - Options - Addons - Browse online and then searching ClientQuery and installing it
- start the bot once by executing the main.py file in the ts3musicbot dir which will create the data folder inside it with a config file and then close it.
- Open the config.json file and fill in the apikey which can be found in your teamspeak client at: tools - options - addons - clientquery - settings optionally change the nickname of the bot and add a default server address and teamspeak path to automatically start teamspeak.
