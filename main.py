@bot.tree.command(name="produtos")
async def produtos(interaction: Interaction):
    with open("produtos.json", "r", encoding="utf-8") as f:
        produtos = json.load(f)
    embed = discord.Embed(title="🛒 Serviços disponíveis", color=0x2ecc71)
    for p in produtos:
        embed.add_field(
            name=f"{p['nome']} – R$ {p['preco']:.2f}",
            value=p["descricao"],
            inline=False
        )
    await interaction.response.send_message(embed=embed)
