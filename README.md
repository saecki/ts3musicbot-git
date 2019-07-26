# ts3musicbot

##Command Line Interface (CLI)

### Usage
To use the bot just write a command in the channel the bot is currently inside.

### Syntax
Commands are built upon a structure.
A command can take certain arguments with or without values attached to them. If an argument requires a value it ends with a colon.
An example command could look like this:

!command arg1: value1 arg2 arg3: value3

### Commands
\* songs can be youtube urls or just text which will be used to search a song on youtube	

| Function                                           | Command |
| ---                                                | --- | 
| adding a song to the queue                         | !play \<song*> |
| playing a song right after the current song        | !playnext \<song*> |
| playing a song right now                           | !playnow \<song*> |
| playing a song at a certain index in the queue     | !playqueue \<index> |
| resuming the song                                  | !play |
| removing the song at a certain index               | !remove \<index> |
| removing the next song                             | !removenext |
| removing the current song                          | !removecurrent |
| pausing the song                                   | !pause |
| playing the next song                              | !next |
| playing the previous song                          | !prev |
| stopping the song                                  | !stop |
| clearing the queue                                 | !clear |
| repeating one song                                 | !repeate |
| repeating all songs                                | !repeate all |
| stop repeating                                     | !repeate stop |
| shuffling the queue                                | !shuffle |
| listing the queue                                  | !list |
|                                                    |
| creating a playlist                                | !playlist create: \<name> |
| creating a playlist from the queue                 | !playlist create: \<name> from: queue |
| creating a playlist from another playlist          | !playlist create: \<name> from: \<otherplaylist> |
| deleteting a playlist                              | !playlist delete: \<name> |
| adding a song to a playlist                        | !playlist add: \<url> to: \<name> |
| removing a song at a certain index from a playlist | !playlist remove: \<index> from: \<name> |
| adding the playlist to the queue                   | !playlist queue: \<name> |
| replacing the queue with a playlist                | !playlist queue: \<name> replace |
| shuffling a playlist                               | !playlist shuffle: \<name> |
| clearing a playlist                                | !playlist clear: \<name> |
| listing all playlists                              | !playlist list: all |
| listing a playlist                                 | !playlist list: \<name> |
