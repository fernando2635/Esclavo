# bot.py
import discord
from discord.ext import commands
from discord.utils import get
import youtube_dl
import random
import requests
import os
from dotenv import load_dotenv

# Cargar el token desde el archivo .env
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

# Configuración del bot
intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents)

# Bot de Música: Reproduce música desde YouTube
@bot.command(name='play', help='Reproduce música desde YouTube')
async def play(ctx, url: str):
    if not ctx.message.author.voice:
        await ctx.send("¡Debes estar en un canal de voz para usar este comando!")
        return
    
    channel = ctx.message.author.voice.channel
    voice_client = get(bot.voice_clients, guild=ctx.guild)
    
    if voice_client is None:
        await channel.connect()
        voice_client = get(bot.voice_clients, guild=ctx.guild)
    
    ydl_opts = {'format': 'bestaudio', 'noplaylist': 'True'}
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        url2 = info['formats'][0]['url']
        voice_client.play(discord.FFmpegPCMAudio(url2))
        await ctx.send(f"Reproduciendo: {info['title']}")

# Bot de Imágenes: Busca y muestra imágenes
@bot.command(name='imagen', help='Busca y muestra imágenes de Unsplash')
async def imagen(ctx, *, query: str):
    client_id = "TU_CLIENT_ID_UNSPLASH"
    response = requests.get(f"https://api.unsplash.com/photos/random?query={query}&client_id={client_id}")
    data = response.json()
    image_url = data['urls']['small']
    await ctx.send(f"Imagen relacionada con '{query}': {image_url}")

# Bot de Reacciones: Reacciona a mensajes con emojis
@bot.event
async def on_message(message):
    if 'hola bot' in message.content.lower():
        await message.add_reaction('👋')
        await message.channel.send('¡Hola! ¿Cómo estás?')
    await bot.process_commands(message)

# Bot de Encuestas: Crea encuestas rápidas
@bot.command(name='encuesta', help='Crea una encuesta rápida')
async def encuesta(ctx, *, pregunta: str):
    message = await ctx.send(f"📊 Encuesta: {pregunta}")
    await message.add_reaction('👍')
    await message.add_reaction('👎')

# Roles Personalizados: Crea roles personalizados
@bot.command(name='rol', help='Crea un rol con un nombre personalizado')
async def rol(ctx, *, nombre: str):
    guild = ctx.guild
    await guild.create_role(name=nombre, color=discord.Color.random())
    await ctx.send(f"Rol creado: {nombre}")

# Emotes personalizados: Agrega emotes al servidor
@bot.command(name='emote', help='Agrega un emote personalizado al servidor')
async def emote(ctx, nombre: str, url: str):
    guild = ctx.guild
    async with ctx.typing():
        img = requests.get(url).content
        await guild.create_custom_emoji(name=nombre, image=img)
    await ctx.send(f"Emote `{nombre}` añadido!")

# Generador de insultos (amistosos)
@bot.command(name='insulto', help='Genera un insulto amistoso')
async def insulto(ctx):
    insultos = ['¡Eres más lento que una tortuga en patines!', '¡No eres la persona más brillante del cuarto, ¿verdad?!', '¡Eres tan brillante como un agujero negro!']
    await ctx.send(random.choice(insultos))

# Memes aleatorios: Envía memes al azar
@bot.command(name='meme', help='Envía un meme aleatorio')
async def meme(ctx):
    response = requests.get('https://meme-api.com/gimme')
    meme_url = response.json()['url']
    await ctx.send(meme_url)

# Iniciar el bot
bot.run(TOKEN)
