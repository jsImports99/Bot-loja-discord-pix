from keep_alive import keep_alive
import discord
from discord.ext import commands
import json, os, dotenv

dotenv.load_dotenv()

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    try:
        synced = await bot.tree.sync()
        print(f"Sincronizado {len(synced)} comando(s)")
    except Exception as e:
        print(f"Erro ao sincronizar: {e}")
    print(f"Bot conectado como {bot.user}")

@bot.tree.command(name="ping")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message("🏓 Pong!")

@bot.tree.command(name="produtos")
async def produtos(interaction: discord.Interaction):
    with open("produtos.json", "r", encoding="utf-8") as f:
        produtos = json.load(f)
    embed = discord.Embed(title="🛒 Produtos disponíveis", color=0x00ff00)
    for p in produtos:
        embed.add_field(name=p["nome"], value=f"💲 R$ {p['preco']:.2f}\n{p['descricao']}", inline=False)
    await interaction.response.send_message(embed=embed)

keep_alive()
bot.run(os.getenv("DISCORD_TOKEN"))
