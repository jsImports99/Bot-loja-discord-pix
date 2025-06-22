import discord from discord.ext import commands from discord import app_commands, Interaction, SelectOption from keep_alive import keep_alive  # Mantenha o bot online no Render import os

intents = discord.Intents.default() bot = commands.Bot(command_prefix="!", intents=intents)

SERVICOS = [ ("1Dungeon M/Normal", 0.50, "\U0001F6D2"), ("1Dungeon M/Desafio", 0.70, "🔥"), ("Geminhas 63", 15.00, "💎"), ("Fenda do medo", 20.00, "🤯"), ("Fenda anciã", 40.00, "🔥"), ("Fazer/Arrumar build", 50.00, "⚒️"), ("Piloto PVP - Pegar lenda", 100.00, "⚔️"), ]

carrinhos = {}

class SelectServico(discord.ui.Select): def init(self): options = [ SelectOption(label=nome, description=f"R$ {preco:.2f}", emoji=emoji, value=nome) for nome, preco, emoji in SERVICOS ] super().init( placeholder="Escolha um serviço", min_values=1, max_values=1, options=options, custom_id="select_servico" )

async def callback(self, interaction: Interaction):
    user_id = interaction.user.id
    servico_escolhido = self.values[0]
    preco = next(p for nome, p, _ in SERVICOS if nome == servico_escolhido)

    if user_id not in carrinhos:
        carrinhos[user_id] = []

    carrinhos[user_id].append((servico_escolhido, preco))
    await interaction.response.send_message(f"✅ {servico_escolhido} adicionado ao carrinho!", ephemeral=True)

class ComprarView(discord.ui.View): def init(self): super().init(timeout=None) self.add_item(SelectServico())

@discord.ui.button(label="✅ Finalizar Compra", style=discord.ButtonStyle.success, custom_id="finalizar")
async def finalizar_compra(self, interaction: Interaction, button: discord.ui.Button):
    user_id = interaction.user.id
    if user_id not in carrinhos or not carrinhos[user_id]:
        await interaction.response.send_message("Seu carrinho está vazio!", ephemeral=True)
        return

    itens = carrinhos[user_id]
    resumo = "\n".join([f"- {nome} — R$ {preco:.2f}" for nome, preco in itens])
    total = sum(preco for _, preco in itens)

    embed = discord.Embed(
        title="📃 Resumo do Pedido:",
        description=f"{resumo}\n\n💰 **Total: R$ {total:.2f}**",
        color=0x2ecc71
    )
    await interaction.response.send_message(embed=embed, ephemeral=True)
    carrinhos[user_id] = []  # Limpa carrinho após resumo

@bot.tree.command(name="comprar", description="Escolha produtos para comprar") async def comprar(interaction: Interaction): embed = discord.Embed( title="🛋️ Escolha os serviços abaixo e defina a quantidade.", description="Finalize com o botão verde!", color=0x3498db ) await interaction.response.send_message(embed=embed, view=ComprarView(), ephemeral=True)

@bot.event async def on_ready(): await bot.tree.sync() print(f"Bot conectado como {bot.user}")

keep_alive()

Use seu token direto ou com variável de ambiente

bot.run(os.getenv("DISCORD_TOKEN"))

