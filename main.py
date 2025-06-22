import os, json, dotenv
import discord
from discord.ext import commands
from discord import app_commands, ButtonStyle, Interaction
from discord.ui import View, Button
from keep_alive import keep_alive

# Carregar variáveis do .env
dotenv.load_dotenv()

# Intents e configuração do bot
intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

# Evento ao iniciar o bot
@bot.event
async def on_ready():
    try:
        synced = await bot.tree.sync()
        print(f"✅ {len(synced)} comando(s) sincronizado(s).")
    except Exception as e:
        print(f"Erro ao sincronizar comandos: {e}")
    print(f"🤖 Bot conectado como {bot.user}")

# Comando básico de teste
@bot.tree.command(name="ping", description="Verifica se o bot está online")
async def ping(interaction: Interaction):
    await interaction.response.send_message("🏓 Pong!")

# Comando para mostrar produtos com embed profissional
@bot.tree.command(name="produtos", description="Veja todos os serviços disponíveis na loja")
async def produtos(interaction: Interaction):
    with open("produtos.json", "r", encoding="utf-8") as f:
        produtos = json.load(f)

    embed = discord.Embed(
        title="🛒 Junior Service - Catálogo de Serviços",
        description="Confira abaixo todos os serviços disponíveis e seus valores.",
        color=0x00ff99
    )
    embed.set_footer(text="Use /comprar <nome do produto> para iniciar sua compra.")

    for p in produtos:
        embed.add_field(
            name=f"🔹 {p['nome']}",
            value=f"💵 **Valor:** R$ {p['preco']:.2f}\n📝 {p['descricao']}",
            inline=False
        )

    await interaction.response.send_message(embed=embed)

# Comando para comprar com botão de pagamento Pix
@bot.tree.command(name="comprar", description="Escolha um produto e receba o botão de pagamento Pix")
@app_commands.describe(produto="Digite o nome EXATO do produto como aparece no /produtos")
async def comprar(interaction: Interaction, produto: str):
    with open("produtos.json", "r", encoding="utf-8") as f:
        produtos = json.load(f)

    item = next((p for p in produtos if p["nome"].lower() == produto.lower()), None)
    if not item:
        await interaction.response.send_message("❌ Produto não encontrado. Verifique o nome com /produtos.")
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
        f"🧾 **{item['nome']}**\n💵 Valor: R$ {item['preco']:.2f}",
        view=view
    )

# Manter bot online (ex: Render)
keep_alive()
bot.run(os.getenv("DISCORD_TOKEN"))
