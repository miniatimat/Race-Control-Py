import os
from dotenv import load_dotenv
import discord
from discord.ext import commands
from discord import app_commands
import functions

load_dotenv()
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
SERVER_ID = os.getenv('SERVER_ID')

bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())


@bot.event
async def on_ready():
    print(f"{bot.user.display_name} is online")

@bot.tree.command(name="say")
@app_commands.describe(thing_to_say="What should I say?")
async def say(interaction: discord.Interaction, thing_to_say: str):
    await interaction.response.send_message(f" {interaction.user.name} said: {thing_to_say}")


@bot.tree.command(name="rank", description="Displays someone's rank")
@app_commands.describe(epic_name="Epic Display Name")
async def say(interaction: discord.Interaction, epic_name: str):
    response = await functions.get_rank(epic_name)
    await interaction.response.send_message(f"{response}")

@bot.tree.command(name='sync', description='Owner only')
async def sync(interaction: discord.Interaction):
    if interaction.user.id == 511161853028728884:
        await bot.tree.sync()
        print('Command tree synced.')
    else:
        await interaction.response.send_message('You must be the owner to use this command!')


bot.run(DISCORD_TOKEN)
