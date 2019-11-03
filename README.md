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
- [Startup Parameters](#startup-parameters)
- [Dependencies](#dependencies)
- [Setup](#setup)

## Command Line Interface

### Usage
To control the bot on teamspeak send a command to the the bot or a channel it is currently inside.  

### Syntax
Commands are built upon a structure.
A command starts with a keyword and can be followed up by certain arguments seperated with spaces which further specify the behavior of the command.  
Arguments on their own can require values, if so they will end with a colon and the values will need to be specified behind them, seperated by spaces aswell.  
Depending on the platform commands can have prefixes to which the command keywords are simply appended.  

An example command for teamspeak could look like this:  
```!command arg1: value1 arg2 arg3: value3```

### Prefixes
| Plattform | Prefix |
| ---       | --- |
| Teamspeak | ! or : |
| Terminal  | ```None``` |

### Commands 
| Function                                                    | Command |
| ---                                                         | --- |
| adding a song to the queue                                  | ```prefix```play ```song*``` |
| playing a song right after the current song                 | ```prefix```playnext ```song*``` |
| playing a song right now                                    | ```prefix```playnow ```song*``` |
| playing a song at a certain index in the queue              | ```prefix```playqueue ```index``` |
| resuming the song                                           | ```prefix```play |
| removing the song at a certain index                        | ```prefix```remove ```index``` |
| removing the next song                                      | ```prefix```removenext |
| removing the current song                                   | ```prefix```removecurrent |
| pausing the song                                            | ```prefix```pause |
| toggling the playback state                                 | ```prefix```toggle |
| playing the next song                                       | ```prefix```next |
| playing the previous song                                   | ```prefix```prev |
| stopping the song                                           | ```prefix```stop |
| clearing the queue                                          | ```prefix```clear |
| repeating one song                                          | ```prefix```repeat |
| repeating all songs                                         | ```prefix```repeat all |
| stop repeating                                              | ```prefix```repeat stop |
| shuffling the queue                                         | ```prefix```shuffle |
| listing the queue                                           | ```prefix```list |
| setting the playback position in percent                    | ```prefix```position ```value```|
| adding a value to the position                              | ```prefix```position ```+value```|
| subtracting a value from the position                       | ```prefix```position ```-value```|
| setting the playback speed in percent                       | ```prefix```speed ```value```|
| adding a value to the speed                                 | ```prefix```speed ```+value```|
| subtracting a value from the speed                          | ```prefix```speed ```-value```|
| setting the volume to a value between 0 to 120              | ```prefix```volume ```value```|
| adding a value to the volume                                | ```prefix```volume ```+value```|
| subtracting a value from the volume                         | ```prefix```volume ```-value```|
|                                                             |
| creating a playlist                                         | ```prefix```playlist create: ```name``` |
| creating a playlist from the queue                          | ```prefix```playlist create: ```name``` from: queue |
| creating a playlist from another playlist                   | ```prefix```playlist create: ```name``` from: ```playlist``` |
| deleteting a playlist                                       | ```prefix```playlist delete: ```name``` |
| adding a song to a playlist                                 | ```prefix```playlist add: ```song*``` to: ```name``` |
| adding a song at a certain index of the queue to a playlist | ```prefix```playlist add: ```index``` to: ```name``` |
| adding the current song to a playlist                       | ```prefix```playlist add: currentsong to: ```name``` |
| adding the queue to a playlist                              | ```prefix```playlist add: queue to: ```name``` |
| adding a playlist to another playlist                       | ```prefix```playlist add: ```playlist``` to: ```name``` |
| removing a song at a certain index from a playlist          | ```prefix```playlist remove: ```index``` from: ```name``` |
| adding the playlist to the queue                            | ```prefix```playlist queue: ```name``` |
| replacing the queue with a playlist                         | ```prefix```playlist play: ```name``` |
| shuffling a playlist                                        | ```prefix```playlist shuffle: ```name``` |
| clearing a playlist                                         | ```prefix```playlist clear: ```name``` |
| listing all playlists                                       | ```prefix```playlist list: all |
| listing a playlist                                          | ```prefix```playlist list: ```name``` |
|                                                             |
| make the bot join your channel                              | ```prefix```comeover |

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

## Startup Parameters
The bots functionality is provided by modules which can be enabled through startup parameters.  
These parameters have to be specified after the main.py file when executing.  
An example could look like this:  
```python3 main.py ctz```

| Module    | Parameter | Function |
| ---       | ---       | --- |
| CLI       | c         | provides a direct command line interface in the terminal |
| Teamspeak | t         | provides a command line interface through teamspeak chat messages |
| ZMQ       | z         | provides a command line interface through a zmq server which can be locally accessed through the zmqinterface.py script in the tools dir |
| Debug     | d         | provides debug functionality and logs |
| Silent    | s         | writes all text output to a log file |

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
- Start the bot once by executing the main.py file in the ts3musicbot dir which will create the data folder inside it with a config file and then close it.
- Open the config.json file and fill in the apikey which can be found in your teamspeak client at: tools - options - addons - clientquery - settings.
- Optionally change the nickname of the bot and add a default server address aswell as a teamspeak path to automatically start teamspeak.
