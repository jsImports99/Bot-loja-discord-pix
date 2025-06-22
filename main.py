import os, json, dotenv
import discord
from discord.ext import commands
from discord import app_commands, ButtonStyle, Interaction
from discord.ui import View, Button
from keep_alive import keep_alive

dotenv.load_dotenv()

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

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
    resposta = "**Produtos disponíveis:**\\n"
    for p in produtos:
        resposta += f"- {p['nome']} - R$ {p['preco']:.2f}\\n"
    await interaction.response.send_message(resposta)

@bot.tree.command(name="comprar")
@app_commands.describe(produto="Nome do produto")
async def comprar(interaction: Interaction, produto: str):
    with open("produtos.json", "r", encoding="utf-8") as f:
        produtos = json.load(f)

    item = next((p for p in produtos if p["nome"].lower() == produto.lower()), None)
    if not item:
        await interaction.response.send_message("❌ Produto não encontrado.")
        return

    pagar_button = Button(label="Pagar com Pix", style=ButtonStyle.success)

    async def button_callback(i: Interaction):
        await i.response.send_message(
            f"💸 Gere seu pagamento Pix:\nhttps://pix.exemplo.com/{item['nome'].replace(' ', '_')}",
            ephemeral=True
        )

    pagar_button.callback = button_callback

    view = View()
    view.add_item(pagar_button)

    await interaction.response.send_message(
        f"Produto: **{item['nome']}**\\nPreço: R$ {item['preco']:.2f}",
        view=view
    )

keep_alive()
bot.run(os.getenv("DISCORD_TOKEN"))
