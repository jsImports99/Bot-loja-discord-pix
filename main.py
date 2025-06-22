from keep_alive import keep_alive
keep_alive()

import discord
from discord.ext import commands, tasks
from discord.ui import View, Button, Select
from dotenv import load_dotenv
import os
import mercadopago
import qrcode
from io import BytesIO

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

carrinhos = {}  # user_id: {"produto": quantidade}

produtos = {
    "🧱 Dungeon M/Normal": 0.50,
    "🪨 Dungeon M/Desafio": 0.70,
    "💎 Geminhas 63": 15.00,
    "😱 Fenda do medo": 20.00,
    "🔥 Fenda anciã": 40.00,
    "🛠️ Fazer/Arrumar build": 50.00,
    "⚔️ Piloto PVP - Pegar lenda": 100.00
}

class ProdutoSelect(Select):
    def __init__(self, user_id):
        options = [
            discord.SelectOption(label=nome, description=f"Valor: R$ {valor:.2f}")
            for nome, valor in produtos.items()
        ]
        super().__init__(placeholder="Escolha um serviço", options=options)
        self.user_id = user_id

    async def callback(self, interaction):
        await interaction.response.send_modal(QuantidadeModal(self.values[0], self.user_id))

class QuantidadeModal(discord.ui.Modal, title="Quantidade do Serviço"):
    def __init__(self, produto, user_id):
        super().__init__()
        self.produto = produto
        self.user_id = user_id
        self.add_item(discord.ui.InputText(label="Quantidade", placeholder="Ex: 2"))

    async def on_submit(self, interaction):
        qtd = int(self.children[0].value)
        carrinho = carrinhos.get(self.user_id, {})
        carrinho[self.produto] = carrinho.get(self.produto, 0) + qtd
        carrinhos[self.user_id] = carrinho
        await interaction.response.send_message(f"✅ Adicionado {qtd}x {self.produto} ao carrinho.", ephemeral=True)

class CarrinhoView(View):
    def __init__(self, user_id):
        super().__init__(timeout=None)
        self.user_id = user_id
        self.add_item(ProdutoSelect(user_id))
        self.add_item(FinalizarButton(user_id))

class FinalizarButton(Button):
    def __init__(self, user_id):
        super().__init__(label="✅ Finalizar Compra", style=discord.ButtonStyle.success)
        self.user_id = user_id

    async def callback(self, interaction):
        carrinho = carrinhos.get(self.user_id)
        if not carrinho:
            await interaction.response.send_message("🛒 Seu carrinho está vazio!", ephemeral=True)
            return

        total = sum(produtos[p] * qtd for p, qtd in carrinho.items())
        resumo = "\n".join([f"{qtd}x {p} - R$ {produtos[p]*qtd:.2f}" for p, qtd in carrinho.items()])

        sdk = mercadopago.SDK(os.getenv("MERCADO_PAGO_TOKEN"))
        payment_data = {
            "transaction_amount": float(total),
            "description": "Pedido na loja Discord",
            "payment_method_id": "pix",
            "payer": {"email": f"{interaction.user.id}@botdiscord.com"}
        }
        pagamento = sdk.payment().create(payment_data)["response"]
        link = pagamento["point_of_interaction"]["transaction_data"]["ticket_url"]
        copia_cola = pagamento["point_of_interaction"]["transaction_data"]["qr_code"]
        id_pagamento = pagamento["id"]

        # QR Code
        qr = qrcode.make(copia_cola)
        buf = BytesIO()
        qr.save(buf, format="PNG")
        buf.seek(0)
        file = discord.File(buf, filename="qrcode.png")

        await interaction.response.send_message(
            f"🧾 **Resumo do Pedido:**\n{resumo}\n\n💰 Total: R$ {total:.2f}\n\n"
            f"📎 Clique aqui para pagar: {link}\n📄 Copia e Cola: `{copia_cola}`",
            file=file,
            ephemeral=True
        )

        monitorar_pagamento.start(id_pagamento, interaction.user.id, resumo, total)
        carrinhos[self.user_id] = {}

@tasks.loop(count=1)
async def monitorar_pagamento(id_pagamento, user_id, resumo, total):
    await bot.wait_until_ready()
    sdk = mercadopago.SDK(os.getenv("MERCADO_PAGO_TOKEN"))
    for _ in range(15):  # tenta por 15 ciclos (~3min)
        pagamento = sdk.payment().get(id_pagamento)["response"]
        if pagamento["status"] == "approved":
            canal = discord.utils.get(bot.get_all_channels(), name="vendas")
            if canal:
                user = await bot.fetch_user(user_id)
                await canal.send(f"✅ **Novo pagamento aprovado!**\n👤 Cliente: {user.name}\n💬 Pedido: {resumo}\n💰 Total: R$ {total:.2f}")
            break
        await discord.utils.sleep_until(discord.utils.utcnow() + discord.utils.timedelta(seconds=12))

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"🤖 Bot online como {bot.user}")

@bot.tree.command(name="comprar", description="Abrir a loja de serviços")
async def comprar(interaction: discord.Interaction):
    await interaction.response.send_message(
        "🛍️ **Escolha os serviços abaixo e defina a quantidade.** Finalize com o botão verde!",
        view=CarrinhoView(interaction.user.id),
        ephemeral=True
    )

bot.run(os.getenv("DISCORD_TOKEN"))