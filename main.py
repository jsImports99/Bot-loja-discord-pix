import discord
from discord.ext import commands
from discord.ui import View, Button

intents = discord.Intents.default()
bot = commands.Bot(command_prefix='!', intents=intents)

# Carrinho temporário por usuário
carrinhos = {}

# Produtos disponíveis
produtos = [
    ("🧱 1Dungeon M/Normal", 0.50),
    ("🪨 1Dungeon M/Desafio", 0.70),
    ("💎 Geminhas 63", 15.00),
    ("😱 Fenda do medo", 20.00),
    ("🔥 Fenda anciã", 40.00),
    ("🛠️ Fazer/Arrumar build", 50.00),
    ("⚔️ Piloto PVP - Pegar lenda", 100.00)
]

class CarrinhoView(View):
    def __init__(self, user_id):
        super().__init__(timeout=None)
        self.user_id = user_id
        for nome, valor in produtos:
            self.add_item(ProdutoButton(label=f"{nome} (R$ {valor:.2f})", produto=(nome, valor)))
        self.add_item(FinalizarButton())

class ProdutoButton(Button):
    def __init__(self, label, produto):
        super().__init__(label=label, style=discord.ButtonStyle.secondary)
        self.produto = produto

    async def callback(self, interaction: discord.Interaction):
        user_id = interaction.user.id
        if user_id not in carrinhos:
            carrinhos[user_id] = []
        carrinhos[user_id].append(self.produto)
        await interaction.response.send_message(
            f"✅ **{self.produto[0]}** adicionado ao carrinho!",
            ephemeral=True
        )

class FinalizarButton(Button):
    def __init__(self):
        super().__init__(label="✅ Finalizar Compra", style=discord.ButtonStyle.success)

    async def callback(self, interaction: discord.Interaction):
        user_id = interaction.user.id
        if user_id not in carrinhos or len(carrinhos[user_id]) == 0:
            await interaction.response.send_message("🛒 Seu carrinho está vazio!", ephemeral=True)
            return

        resumo = ""
        total = 0
        for nome, valor in carrinhos[user_id]:
            resumo += f"• {nome} — R$ {valor:.2f}\n"
            total += valor

        await interaction.response.send_message(
            f"🛍️ **Resumo do seu pedido:**\n\n{resumo}\n💰 **Total: R$ {total:.2f}**\n\n"
            "📲 Aguarde o pagamento ser gerado via Pix automático.",
            ephemeral=True
        )
        carrinhos[user_id] = []

@bot.event
async def on_ready():
    print(f"✅ Bot conectado como {bot.user}")
    try:
        synced = await bot.tree.sync()
        print(f"📌 {len(synced)} comandos sincronizados.")
    except Exception as e:
        print(f"Erro ao sincronizar comandos: {e}")

@bot.tree.command(name="comprar", description="Abrir o menu de compra dos serviços")
async def comprar(interaction: discord.Interaction):
    embed = discord.Embed(
        title="🛒 Loja de Serviços",
        description="Clique nos botões abaixo para adicionar produtos ao carrinho.\nFinalize quando estiver pronto!",
        color=discord.Color.blurple()
    )
    embed.set_footer(text="JS IMPORT'S | Discord Bot Store")
    embed.set_thumbnail(url="https://cdn-icons-png.flaticon.com/512/891/891419.png")  # Ícone opcional

    await interaction.response.send_message(embed=embed, view=CarrinhoView(interaction.user.id), ephemeral=True)

# Iniciar o bot
bot.run("SEU_TOKEN_AQUI")
