from keep_alive import keep_alive
keep_alive()

import discord
from discord.ext import commands
from discord import app_commands, Interaction, SelectOption
from keep_alive import keep_alive
import os

TOKEN = os.getenv("DISCORD_TOKEN")
intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

# Produtos disponíveis
produtos = {
    "1Dungeon M/Normal": 0.50,
    "1Dungeon M/Desafio": 0.70,
    "Geminhas 63": 15.00,
    "Fenda do medo": 20.00,
    "Fenda anciã": 40.00,
    "Fazer build / Arrumar build": 50.00,
    "Piloto PVP - Pegar lenda": 100.00,
}

user_carrinho = {}

class ProdutoSelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label=nome, description=f"R$ {valor:.2f}", value=nome)
            for nome, valor in produtos.items()
        ]
        super().__init__(placeholder="Escolha um serviço", options=options, min_values=1, max_values=1)

    async def callback(self, interaction: Interaction):
        usuario = interaction.user.id
        produto = self.values[0]
        if usuario not in user_carrinho:
            user_carrinho[usuario] = {}
        user_carrinho[usuario][produto] = user_carrinho[usuario].get(produto, 0) + 1
        await interaction.response.send_message(f"✅ {produto} adicionado ao carrinho!", ephemeral=True)

class ProdutoView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(ProdutoSelect())

@bot.tree.command(name="comprar")
async def comprar(interaction: Interaction):
    embed = discord.Embed(
        title="🛍️ Escolha os serviços abaixo e defina a quantidade",
        description="Finalize com o botão verde!",
        color=0x00ff00
    )
    view = ProdutoView()
    view.add_item(FinalizarButton())
    await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

class FinalizarButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label="✅ Finalizar Compra", style=discord.ButtonStyle.success)

    async def callback(self, interaction: Interaction):
        usuario = interaction.user.id
        if usuario not in user_carrinho or not user_carrinho[usuario]:
            await interaction.response.send_message("🛒 Seu carrinho está vazio!", ephemeral=True)
            return

        itens = user_carrinho[usuario]
        total = sum(produtos[n] * q for n, q in itens.items())
        lista = "\n".join([f"• {n} x{q} — R$ {produtos[n]*q:.2f}" for n, q in itens.items()])
        resumo = f"🧾 **Resumo do Pedido:**\n{lista}\n\n💰 **Total: R$ {total:.2f}**"

        embed = discord.Embed(title="📦 Pedido Finalizado", description=resumo, color=0x00ff00)
        await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"✅ {bot.user} conectado.")
    try:
        keep_alive()
    except:
        pass

bot.run(TOKEN)bot.run(os.getenv("DISCORD_TOKEN"))
