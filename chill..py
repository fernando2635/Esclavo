# Importa las bibliotecas necesarias
import discord
from discord.ext import commands
from discord.utils import get
import youtube_dl
import os
from dotenv import load_dotenv

# Cargar el token desde el archivo .env
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN2')

# Configuración del bot
intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents)

# Cola de reproducción para almacenar las canciones
song_queue = []

# Reproduce música desde YouTube y permanece en el canal de voz
@bot.command(name='play', help='Reproduce música desde YouTube de forma continua')
async def play(ctx, url: str):
    if not ctx.message.author.voice:
        await ctx.send("¡Debes estar en un canal de voz para usar este comando!")
        return
    
    channel = ctx.message.author.voice.channel
    voice_client = get(bot.voice_clients, guild=ctx.guild)
    
    # Conéctate al canal de voz si no está conectado
    if voice_client is None:
        await channel.connect()
        voice_client = get(bot.voice_clients, guild=ctx.guild)
    
    # Agrega la canción a la cola
    song_queue.append(url)
    
    # Si no está reproduciendo, reproduce la siguiente canción
    if not voice_client.is_playing():
        await play_next_song(ctx, voice_client)

# Función para reproducir la siguiente canción en la cola
async def play_next_song(ctx, voice_client):
    if len(song_queue) > 0:
        url = song_queue.pop(0)  # Extrae la primera canción de la cola

        # Descargar la canción con youtube_dl
        ydl_opts = {'format': 'bestaudio', 'noplaylist': 'True'}
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            url2 = info['formats'][0]['url']
            title = info['title']
        
        # Reproduce la canción
        voice_client.play(discord.FFmpegPCMAudio(url2), after=lambda e: bot.loop.create_task(play_next_song(ctx, voice_client)))
        await ctx.send(f"Reproduciendo: {title}")
    else:
        # Si la cola está vacía, permanecer en el canal de voz
        await ctx.send("La cola está vacía. Añade más canciones con `!play <url>`.")

# Comando para desconectar al bot manualmente
@bot.command(name='disconnect', help='Desconecta al bot del canal de voz')
async def disconnect(ctx):
    voice_client = get(bot.voice_clients, guild=ctx.guild)
    if voice_client and voice_client.is_connected():
        await voice_client.disconnect()
        await ctx.send("Desconectado del canal de voz.")
    else:
        await ctx.send("El bot no está conectado a ningún canal de voz.")

# Iniciar el bot
bot.run(TOKEN)
