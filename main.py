import os
import json
import discord
from discord.ext import commands
from discord import app_commands, Interaction, ButtonStyle
from discord.ui import View, Button
from keep_alive import keep_alive
import requests
import base64
import io

dotenv_path = ".env"
if os.path.exists(dotenv_path):
    from dotenv import load_dotenv
    load_dotenv(dotenv_path)

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)
user_carts = {}

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"✅ Bot conectado como {bot.user}")

def carregar_produtos():
    with open("produtos.json", "r", encoding="utf-8") as f:
        return json.load(f)

def gerar_total(carrinho):
    total = 0.0
    for item in carrinho:
        total += item["preco"] * item["quantidade"]
    return total

class ProdutoView(View):
    def __init__(self, user_id):
        super().__init__(timeout=None)
        self.user_id = user_id
        self.produtos = carregar_produtos()
        for p in self.produtos:
            self.add_item(ProdutoBotao(p["nome"], p["preco"], user_id))

        self.add_item(FinalizarCompraButton(user_id))

class ProdutoBotao(Button):
    def __init__(self, nome, preco, user_id):
        super().__init__(label=f"{nome} (R$ {preco:.2f})", style=ButtonStyle.secondary)
        self.nome = nome
        self.preco = preco
        self.user_id = user_id

    async def callback(self, interaction: Interaction):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ Esse carrinho não é seu.", ephemeral=True)
            return

        user_cart = user_carts.setdefault(self.user_id, [])
        for item in user_cart:
            if item["nome"] == self.nome:
                item["quantidade"] += 1
                break
        else:
            user_cart.append({"nome": self.nome, "preco": self.preco, "quantidade": 1})

        resumo = "\n".join([f"- {i['quantidade']}x {i['nome']} (R$ {i['preco'] * i['quantidade']:.2f})" for i in user_cart])
        total = gerar_total(user_cart)
        await interaction.response.send_message(
            f"🛒 Produto adicionado ao carrinho!\n\n📦 Carrinho atual:\n{resumo}\n\n💰 Total: R$ {total:.2f}",
            ephemeral=True
        )

class FinalizarCompraButton(Button):
    def __init__(self, user_id):
        super().__init__(label="✅ Finalizar Compra", style=ButtonStyle.success)
        self.user_id = user_id

    async def callback(self, interaction: Interaction):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ Esse carrinho não é seu.", ephemeral=True)
            return

        carrinho = user_carts.get(self.user_id, [])
        if not carrinho:
            await interaction.response.send_message("❗ Seu carrinho está vazio.", ephemeral=True)
            return

        total = gerar_total(carrinho)
        descricao = ", ".join([f"{item['quantidade']}x {item['nome']}" for item in carrinho])

        headers = {
            "Authorization": f"Bearer {os.getenv('MERCADO_PAGO_ACCESS_TOKEN')}",
            "Content-Type": "application/json"
        }

        body = {
            "transaction_amount": total,
            "description": descricao,
            "payment_method_id": "pix",
            "payer": {
                "email": "comprador@email.com"
            },
            "notification_url": os.getenv("WEBHOOK_URL")
        }

        response = requests.post("https://api.mercadopago.com/v1/payments", headers=headers, json=body)
        data = response.json()

        if "point_of_interaction" not in data:
            await interaction.response.send_message("⚠️ Erro ao gerar pagamento Pix.", ephemeral=True)
            return

        qr_code = data["point_of_interaction"]["transaction_data"]["qr_code"]
        qr_image = base64.b64decode(data["point_of_interaction"]["transaction_data"]["qr_code_base64"])

        file = discord.File(io.BytesIO(qr_image), filename="qrcode.png")
        await interaction.response.send_message(
            f"✅ Compra criada!\n\n🧾 **Resumo:** {descricao}\n💰 Total: R$ {total:.2f}\n\nEscaneie o QR Code para pagar ou use o botão abaixo.",
            file=file,
            view=PixCodeView(qr_code)
        )
        user_carts[self.user_id] = []

class PixCodeView(View):
    def __init__(self, qr_code):
        super().__init__()
        self.add_item(PixCodeButton(qr_code))

class PixCodeButton(Button):
    def __init__(self, qr_code):
        super().__init__(label="🔗 Copiar código Pix", style=ButtonStyle.primary)
        self.qr_code = qr_code

    async def callback(self, interaction: Interaction):
        await interaction.response.send_message(f"🔢 Código Pix:\n```{self.qr_code}```", ephemeral=True)

@bot.tree.command(name="comprar")
async def comprar(interaction: Interaction):
    view = ProdutoView(interaction.user.id)
    await interaction.response.send_message(
        "🛍️ Selecione os produtos abaixo para adicionar ao seu carrinho:",
        view=view,
        ephemeral=True
    )

keep_alive()
bot.run(os.getenv("DISCORD_TOKEN"))# Arquivo main.py com suporte a carrinho e botões interativos (será gerado em breve)
