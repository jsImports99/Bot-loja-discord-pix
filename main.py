# IMPORTAÇÕES E CONFIG
import os, json, dotenv
import discord
from discord.ext import commands
from discord import app_commands, ButtonStyle, Interaction
from discord.ui import View, Button
from keep_alive import keep_alive

dotenv.load_dotenv()
intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

# COMANDOS
@bot.event
async def on_ready():
    try:
        synced = await bot.tree.sync()
        print(f"Sincronizado {len(synced)} comando(s)")
    except Exception as e:
        print(f"Erro ao sincronizar comandos: {e}")
    print(f"Bot conectado como {bot.user}")

@bot.tree.command(name="ping")
async def ping(interaction: Interaction):
    await interaction.response.send_message("🏓 Pong!")

@bot.tree.command(name="produtos")
async def produtos(interaction: Interaction):
    with open("produtos.json", "r", encoding="utf-8") as f:
        produtos = json.load(f)
    embed = discord.Embed(title="🛒 Serviços disponíveis", color=0x2ecc71)
    for p in produtos:
        embed.add_field(
            name=f"{p['nome']} – R$ {p['preco']:.2f}",
            value=p["descricao"],
            inline=False
        )
    await interaction.response.send_message(embed=embed)

# ... restante do código (/comprar, etc)

keep_alive()
bot.run(os.getenv("DISCORD_TOKEN"))
