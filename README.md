# Teamspeak3MusicBot

## Usage

### Syntax
command arg1: value1 arg2 arg3: value3


### Commands
| Function                                         | Command |              
| ---                                              | --- | 
| adding a song to the queue                       | !play \<song*> |
| playing a song right after the current song      | !playnext \<song*> |
| playing a song right now                         | !playnow \<song*> |
| playing a song at a certain index in the queue   | !playqueue \<index> |
| resuming the song                                | !play |
| pausing the song                                 | !pause |
| playing the next song                            | !next |
| playing the previous song                        | !prev |
| stopping the song                                | !stop |
| clearing the queue                               | !clear |
| repeating one song                               | !repeate |
| repeating all songs                              | !repeate all |
| stop repeating                                   | !repeate stop |
| shuffling the queue                              | !shuffle |
|                                                  |
| creating a playlist                              | !playlist create: \<name> |
| creating a playlist from the queue               | !playlist create: \<name> from: queue |
| creating a playlist from another playlist        | !playlist create: \<name> from: \<otherplaylist> |
| deleteting a playlist                            | !playlist delete: \<name>
| adding a song to the playlist                    | !playlist add: \<youtube.url> to: \<name> |
| adding the playlist to the queue                 | !playlist queue: \<name> |
| replacing the queue with a playlist              | !playlist queue: \<name> replace |
| shuffling a playlist                             | !playlist shuffle: \<name> |
| clearing a playlist                              | !playlist clear: \<name> |

\* songs can be youtube urls or just text which will be used to search a song on youtube
