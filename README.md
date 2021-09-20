# discord.py-youtube-music

Music bot for Discord with functional queue, written in python. Bot streams music from Youtube, either by a link or a name.

## Dependencies (as of Sep 20, 2021)

For the bot to work you'll need these dependencies, with a working FFMPEG in your path or `FFMPEG.exe` in your project folder. Discord.py version states the minimum version with guilds, tasks and asyncio includes.

- PyNaCl: pip install PyNaCl
- youtube_dl: pip install youtube_dl`

## Bot settings

With the updates from discord, you are required to turn on guilds from you Application Settings over at Discord Developers, since this bot uses guilds.

### Procfile

Heroku procfile uses a worker bot, instead of a webservice, included in the files. If you are not planning to host on Heroku or other hosting services using workers, ignore this file.
