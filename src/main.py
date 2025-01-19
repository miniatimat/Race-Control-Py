import os
from dotenv import load_dotenv
import discord
from discord.ext import commands
from discord import app_commands
import functions
import aiosqlite
import asyncio
import re

load_dotenv()
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
SERVER_ID = os.getenv('SERVER_ID')

bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())
rr_seasons = [
    app_commands.Choice(name="December 2024", value='rrhr6d'),
    app_commands.Choice(name="October 2024", value='rr9qlw'),
    app_commands.Choice(name="Volcano Island", value='rrzuel'),
    app_commands.Choice(name="Neon Rush", value='rrwpwg'),
    app_commands.Choice(name="Season 0", value='dmd372')
]


@bot.event
async def on_ready():
    bot.db = await  aiosqlite.connect('Revive_bot.db')
    c = await bot.db.cursor()
    await c.execute("CREATE TABLE IF NOT EXISTS players(discord_id INTEGER, epic_display_name TEXT, epic_id TEXT, revive_rating INTEGER , validated BOOL)")
    await c.execute("CREATE TABLE IF NOT EXISTS maps(map_code TEXT, map_name TEXT)")
    await bot.db.commit()
    print(f"{bot.user.display_name} is online")

@bot.tree.command(name='sync', description='Owner only')
@commands.is_owner()
@app_commands.describe(apply_to_all='apply to all')
async def sync(interaction: discord.Interaction, apply_to_all: bool = False):
    if not apply_to_all:
        await interaction.response.defer()
        await bot.tree.sync(guild=discord.Object(id=SERVER_ID))
        await interaction.followup.send("Commands Synced successfully for server")
    else:
        await interaction.response.defer()
        await bot.tree.sync()
        await interaction.followup.send("Commands Synced successfully")

@bot.tree.command(name="rank", description="Displays someone's rank")
@app_commands.describe(epic_name="Epic Display Name", season='Season')
@app_commands.choices(season=rr_seasons)
async def say(interaction: discord.Interaction, epic_name: str = None, season: str = rr_seasons[0].value ):
    await interaction.response.defer()
    response = await functions.get_rank(bot, interaction.user.id, epic_name,season)
    await interaction.followup.send(f"{response}")

@bot.tree.command(name="register", description="Register with the bot")
@app_commands.describe(epic_name="Epic Display Name", epic_id="Your Epic Accoutn ID, find it in your account settings on epicgames.com")
async def say(interaction: discord.Interaction, epic_name: str, epic_id: str = None):
    await interaction.response.defer()
    user = await functions.get_user(bot, interaction.user.id)
    if user is not None:
        await interaction.followup.send("You're already registered. You can edit your information with the /edit command")
        return
    try:
        result = await functions.register(bot, interaction.user.id, epic_name, epic_id)
        await interaction.followup.send(result)
    except Exception as e:
        print(e)
        await interaction.followup.send("Something went wrong")

@bot.tree.command(name="edit", description="Edit your details")
@app_commands.describe(epic_name="Epic Display Name", epic_id="Your Epic Accoutn ID, find it in your account settings on epicgames.com")
async def say(interaction: discord.Interaction, epic_name: str = None, epic_id: str = None):
    await interaction.response.defer()
    user = functions.get_player(bot, interaction.user.id)
    if user is None:
        await interaction.followup.send("You're not registered. You can, please do so with the /register command")
        return
    if epic_name is None and epic_id is None:
        await interaction.followup.send("Please add either your epic ID or your display name")
    try:
        result = await functions.edit(bot, interaction.user.id, epic_name, epic_id)
        await interaction.followup.send(result)
    except Exception as e:
        print(e)
        await interaction.followup.send("Something went wrong")

@bot.tree.command(name='add_map', description="Add map to the map pool")
@commands.is_owner()
@app_commands.describe(map_code="Map Code", map_name="Map Name")
async def say(interaction: discord.Interaction, map_code: str, map_name: str):
    await interaction.response.defer()

    # Regular expression pattern for the desired format (4 digits, dash, 4 digits, dash, 4 digits)
    pattern = r'^\d{4}-\d{4}-\d{4}$'
    # Check if the input matches the pattern
    if not re.match(pattern, map_code):
        await interaction.followup.send("Please submit a valid map code")
    response = await functions.add_map(bot, map_code, map_name)
    await interaction.followup.send(response)

@bot.tree.command(name='remove_map', description="Remove map from map pool")
@commands.is_owner()
@app_commands.describe(map_code="Map Code")
async def say(interaction: discord.Interaction, map_code: str):
    await interaction.response.defer()

    # Regular expression pattern for the desired format (4 digits, dash, 4 digits, dash, 4 digits)
    pattern = r'^\d{4}-\d{4}-\d{4}$'
    # Check if the input matches the pattern
    if not re.match(pattern, map_code):
        await interaction.followup.send("Please submit a valid map code")
    response = await functions.remove_map(bot, map_code)
    await interaction.followup.send(response)

@bot.tree.command(name="leaderboard", description="Display the current revive leaderbaord")
async def say(interaction: discord.Interaction):
    await interaction.response.defer()
    result = await functions.leaderboard(bot)
    await interaction.followup.send(result)



bot.run(DISCORD_TOKEN)
asyncio.run(bot.db.close())
