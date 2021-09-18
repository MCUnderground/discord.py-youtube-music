import discord
import os
import youtube_dl
from discord.ext import commands,tasks
import asyncio
import itertools

songQueue = []

tasker = None

bot = commands.Bot(command_prefix='.')

youtube_dl.utils.bug_reports_message = lambda: ''

ytdl_format_options = {
    'format': 'bestaudio/best',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0' # bind to ipv4 since ipv6 addresses cause issues sometimes
}

ffmpeg_options = {
    'options': '-vn'
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get('title')
        self.duration = data.get('duration')
        self.url = ""

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False, play=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(f"ytsearch:{url}", download=not stream or play))

        if 'entries' in data:
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)

@bot.event
async def on_ready():
  print(f'Logged in as {bot.user} (ID: {bot.user.id})')
  print('------')
 

@bot.command(name='leave', help='To make the bot leave the voice channel')
async def leave(ctx):
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_connected():
        await voice_client.disconnect()
    else:
        await ctx.send("The bot is not connected to a voice channel.")

@bot.command(name='play', aliases=['p', 'play_song'], help='To play song')
async def play(ctx, *, url:str):
  global songQueue
  voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
  try :
    if(voice == None):
      if not ctx.message.author.voice:
        await ctx.send("{} is not connected to a voice channel".format(ctx.message.author.name))
      else:
        channel = ctx.message.author.voice.channel
        await channel.connect()

    async with ctx.typing():

      voice_client = ctx.message.guild.voice_client
      if not voice_client.is_playing():
        songQueue.clear()

      player = await YTDLSource.from_url(url, loop=bot.loop, stream=True)
      if len(songQueue) == 0:
        await start_playing(ctx, player)
      else:
        songQueue.append(player)
        await ctx.send('**Queued at position {}:** {}'.format(len(songQueue)-1,player.title))
  except:
      await ctx.send("Error occured.")

async def start_playing(ctx, player):
    global songQueue
    songQueue.append(player)
    global tasker
    if(songQueue[0] == None):
      return
    i = 0
    while i <  len(songQueue):
        try:
            ctx.voice_client.play(songQueue[0], after=lambda e: print('Player error: %s' % e) if e else None)
            await ctx.send('**Now playing:** {}'.format(songQueue[0].title))
        except:
            await ctx.send("Ok")
        #await asyncio.sleep(songQueue[0].duration)
        tasker = asyncio.create_task(coro(ctx,songQueue[0].duration))
        try:
           await tasker
        except asyncio.CancelledError:
          print("Task cancelled")
        if(len(songQueue) > 0):
          songQueue.pop(0)

async def coro(ctx,duration):
  await asyncio.sleep(duration)

@bot.command(name='queued', help='This command pauses the song')
async def queued(ctx):
    global songQueue
    a = ""
    i = 0
    for f in songQueue:
      if i > 0:
       a = a + str(i) +". " + f.title + "\n "
      i += 1
    await ctx.send("Queued songs: \n " + a);

@bot.command(name='pause', help='This command pauses the song')
async def pause(ctx):
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_playing():
        await ctx.send("Paused playing.")
        await voice_client.pause()
    else:
        await ctx.send("The bot is not playing anything at the moment.")
    
@bot.command(name='resume', help='Resumes the song')
async def resume(ctx):
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_paused():
        await ctx.send("Resumed playing.")
        await voice_client.resume()
    else:
        await ctx.send("The bot was not playing anything before this. Use play_song command")

@bot.command(name='stop', help='Stops the song')
async def stop(ctx):
    global tasker
    global songQueue
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_playing():
        songQueue.clear()
        voice_client.stop()
        tasker.cancel()
        await ctx.send("Stopped playing.")
    else:
        await ctx.send("The bot is not playing anything at the moment.")

@bot.command(name='skip', help='Skip the song')
async def skip(ctx):
    global tasker
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_playing():
        voice_client.stop()
        tasker.cancel()
        await ctx.send("Skipped song.")
    else:
        await ctx.send("The bot is not playing anything at the moment.")


bot.run('TOKEN')
