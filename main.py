from keep_alive import keep_alive
keep_alive()

import discord
from discord.ext import commands
from discord import app_commands
from flask import Flask
from threading import Thread
import os

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Keep Alive
app = Flask('')

@app.route('/')
def home():
    return "✅ Bot está online!"

def run():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    Thread(target=run).start()

# Produtos disponíveis
produtos = {
    "1Dungeon M/Normal": 0.50,
    "1Dungeon M/Desafio": 0.70,
    "Geminhas 63": 15.00,
    "Fenda do medo": 20.00,
    "Fenda anciã": 40.00,
    "Fazer/Arrumar build": 50.00,
    "Piloto PVP - Pegar lenda": 100.00,
}

# Carrinho temporário por usuário
carrinhos = {}

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"✅ Bot conectado como {bot.user}")

@bot.tree.command(name="comprar", description="Abrir menu de compra com botões")
async def comprar(interaction: discord.Interaction):
    view = ProdutoView(interaction.user)
    await interaction.response.send_message(
        embed=discord.Embed(
            title="🛍 Escolha os serviços abaixo e defina a quantidade.",
            description="Finalize com o botão verde ✅ Finalizar Compra!",
            color=discord.Color.green()
        ),
        view=view,
        ephemeral=True
    )

class ProdutoView(discord.ui.View):
    def __init__(self, user):
        super().__init__(timeout=300)
        self.user = user
        self.total = 0
        self.carrinho = {}

        for nome, preco in produtos.items():
            self.add_item(ProdutoButton(nome, preco, self))

        self.add_item(FinalizarButton(self))

class ProdutoButton(discord.ui.Button):
    def __init__(self, nome, preco, parent_view):
        super().__init__(label=f"{nome} (R$ {preco:.2f})", style=discord.ButtonStyle.secondary)
        self.nome = nome
        self.preco = preco
        self.parent_view = parent_view

    async def callback(self, interaction: discord.Interaction):
        if interaction.user != self.parent_view.user:
            await interaction.response.send_message("❌ Esse menu não é pra você.", ephemeral=True)
            return
        
        # Adiciona ao carrinho com quantidade
        if self.nome in self.parent_view.carrinho:
            self.parent_view.carrinho[self.nome]["qtd"] += 1
        else:
            self.parent_view.carrinho[self.nome] = {"preco": self.preco, "qtd": 1}

        await interaction.response.send_message(
            f"✅ `{self.nome}` adicionado ao carrinho!", ephemeral=True
        )

class FinalizarButton(discord.ui.Button):
    def __init__(self, parent_view):
        super().__init__(label="✅ Finalizar Compra", style=discord.ButtonStyle.success)
        self.parent_view = parent_view

    async def callback(self, interaction: discord.Interaction):
        if interaction.user != self.parent_view.user:
            await interaction.response.send_message("❌ Esse menu não é pra você.", ephemeral=True)
            return

        carrinho = self.parent_view.carrinho
        if not carrinho:
            await interaction.response.send_message("❗ Carrinho vazio.", ephemeral=True)
            return

        total = 0
        resumo = ""
        for nome, info in carrinho.items():
            subtotal = info["preco"] * info["qtd"]
            total += subtotal
            resumo += f"• {nome} × {info['qtd']} — R$ {subtotal:.2f}\n"

        resumo += f"\n💰 **Total: R$ {total:.2f}**"

        embed = discord.Embed(title="📦 Resumo do Pedido", description=resumo, color=discord.Color.blue())
        await interaction.response.send_message(embed=embed, ephemeral=True)

        # Aqui você pode adicionar a geração de QR Code Pix com base no valor total

# Ativar keep_alive para Render
keep_alive()

# Token
TOKEN = os.getenv("DISCORD_TOKEN")  # Certifique-se de configurar essa variável no Render
bot.run(TOKEN)
