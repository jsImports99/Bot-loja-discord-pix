
import discord
from discord.ext import commands
import json
import os
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

# Carrega os produtos
def carregar_produtos():
    with open("produtos.json", "r", encoding="utf-8") as f:
        return json.load(f)

@bot.event
async def on_ready():
    print(f"Bot conectado como {bot.user}")
    try:
        synced = await bot.tree.sync()
        print(f"Sincronizados {len(synced)} comandos de barra.")
    except Exception as e:
        print(e)

@bot.tree.command(name="produtos", description="Veja os produtos disponíveis")
async def produtos(interaction: discord.Interaction):
    produtos = carregar_produtos()
    embed = discord.Embed(title="🛒 Produtos disponíveis", color=0x00ff00)
    for item in produtos:
        embed.add_field(
            name=f"{item['nome']} - R$ {item['preco']:.2f}",
            value=item['descricao'],
            inline=False
        )
    await interaction.response.send_message(embed=embed)

bot.run(TOKEN)
