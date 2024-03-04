from typing import Final
import os
from dotenv import load_dotenv
import discord
from discord.ext import commands
from discord import app_commands

load_dotenv()
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')

bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())


@bot.event
async def on_ready():
    print(f"{bot.user.display_name} is online")
    try:
        synced = await bot.tree.sync()
        print(f'Synced {len(synced)} command(s)')
    except Exception as e:
        print(e)

@bot.tree.command (name="hello")
async def hello(interaction: discord. Interaction):
    await interaction.response.send_message(f"Hey {interaction.user.mention}! This is a slash command!", ephemeral=True)

@bot.tree.command (name="say")
@app_commands.describe (thing_to_say = "What should I say?")
async def say (interaction: discord. Interaction, thing_to_say: str):
    await interaction.response.send_message(f" {interaction.user.name} said: {thing_to_say}")

bot.run(DISCORD_TOKEN)