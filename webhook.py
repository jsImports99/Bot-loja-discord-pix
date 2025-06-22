from flask import Flask, request
import os, discord
from discord.ext import commands
from threading import Thread

app = Flask(__name__)
client = commands.Bot(command_prefix="!", intents=discord.Intents.default())

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    if data.get("type") == "payment" and data["data"]["status"] == "approved":
        description = data["data"]["description"]
        channel = client.get_channel(int(os.getenv("DISCORD_CHANNEL_ID")))
        if channel:
            client.loop.create_task(channel.send(f"✅ Pagamento aprovado para **{description}**!"))
    return "ok", 200

def run():
    app.run(host="0.0.0.0", port=10000)

def keep_alive():
    t = Thread(target=run)
    t.start()