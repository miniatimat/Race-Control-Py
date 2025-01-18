import os
from dotenv import load_dotenv
import discord
from discord.ext import commands
from discord import app_commands
import functions
import aiosqlite
import asyncio

load_dotenv()
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
SERVER_ID = os.getenv('SERVER_ID')

bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())


@bot.event
async def on_ready():
    bot.db = await  aiosqlite.connect('Revive_bot.db')
    c = await bot.db.cursor()
    await c.execute("CREATE TABLE IF NOT EXISTS players(discord_id INTEGER, epic_display_name TEXT, epic_id TEXT, revive_rating INTEGER )")
    await bot.db.commit()
    print(f"{bot.user.display_name} is online")

@bot.tree.command(name='sync', description='Owner only')
async def sync(interaction: discord.Interaction):
    if interaction.user.id == 511161853028728884:
        await interaction.response.defer()
        await bot.tree.sync(guild=discord.Object(id=SERVER_ID))
        print('Command tree synced.')
        await interaction.followup.send("Commands Synced successfully")
    else:
        await interaction.response.send_message('You must be the owner to use this command!')

@bot.tree.command(name="rank", description="Displays someone's rank")
@app_commands.describe(epic_name="Epic Display Name", season='Season')
@app_commands.choices(season=[
    app_commands.Choice(name="December 2024", value='rrhr6d'),
    app_commands.Choice(name="October 2024", value='rr9qlw'),
    app_commands.Choice(name="Volcano Island", value='rrzuel'),
    app_commands.Choice(name="Neon Rush", value='rrwpwg'),
    app_commands.Choice(name="Season 0", value='dmd372')
    ])
async def say(interaction: discord.Interaction, epic_name: str, season: str):
    await interaction.response.defer()
    response = await functions.get_rank(epic_name,season)
    await interaction.followup.send(f"{response}")

@bot.tree.command(name="register", description="Register with the bot")
@app_commands.describe(epic_name="Epic Display Name")
async def say(interaction: discord.Interaction, epic_name: str):
    await interaction.response.defer()
    c = await bot.db.cursor()
    await c.execute(f"SELECT * FROM players WHERE discord_id = {interaction.user.id}")
    user = await c.fetchone()
    if user is not None:
        await interaction.followup.send("You're already registered. You can edit your information with the /edit command")
        return
    try:
        epic_id = await functions.name_to_id(epic_name)
        sql = f"INSERT INTO players (discord_id, epic_display_name, epic_id, revive_rating) VALUES( {int(interaction.user.id)}, '{epic_name}', '{epic_id}', 1000)"
        await c.execute(sql)
        await bot.db.commit()
        await interaction.followup.send("User registered successfully")
    except Exception as e:
        print(e)
        await interaction.followup.send("Something went wrong")


bot.run(DISCORD_TOKEN)
asyncio.run(bot.db.close())
