import os
from dotenv import load_dotenv
import requests
import aiosqlite

load_dotenv()
DEVICE = os.getenv('DEVICE_ID'),
ACCOUNT = os.getenv('ACCOUNT_ID'),
SECRET = os.getenv('CLIENT_SECRET')

global TOKEN
TOKEN = ""


async def validate_token():
    url = "https://account-public-service-prod.ol.epicgames.com/account/api/oauth/verify"
    headers = {
        "Authorization": f"Bearer {TOKEN}"
    }
    res = requests.get(url, headers=headers)
    res = res.json()
    if "errorCode" in res:
        print("Token is NOT valid")
        return False
    print("Token is valid")
    return True

async def get_token():
    print("Validating token")
    if await validate_token():
        return
    url = 'https://account-public-service-prod.ol.epicgames.com/account/api/oauth/token'
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Authorization": "Basic M2Y2OWU1NmM3NjQ5NDkyYzhjYzI5ZjFhZjA4YThhMTI6YjUxZWU5Y2IxMjIzNGY1MGE2OWVmYTY3ZWY1MzgxMmU="
    }

    data = {
        "grant_type": "device_auth",
        "device_id": DEVICE,
        "account_id": ACCOUNT,
        "secret": SECRET
    }
    res = requests.post(url, headers=headers, data=data)
    res = res.json()
    global TOKEN
    TOKEN = res['access_token']

async def get_external_auth(name):
    auth_types = ['steam', 'psn', 'xbl', 'nintendo']
    for t in auth_types:
        url = f'https://account-public-service-prod.ol.epicgames.com/account/api/public/account/lookup/externalAuth/{t}/displayName/{name}'
        headers = {
            "Authorization": f"Bearer {TOKEN}"
        }
        res = requests.get(url, headers=headers)
        res = res.json()
        if len(res) > 0:
            return res[0]
    return -1


async def name_to_id(name):
    await get_token()
    url = f'https://account-public-service-prod.ol.epicgames.com/account/api/public/account/displayName/{name}'
    headers = {
        "Authorization": f"Bearer {TOKEN}"
    }

    res = requests.get(url, headers=headers)
    res = res.json()
    print(res)
    if 'errorCode' in res:
        res = await get_external_auth(name)
    if res == -1:
        return -1
    return res['id']

async def get_rank(bot, discord_id, name,season):
    await get_token()

    if name is None:
        # Get epic_id from DB
        c = await bot.db.cursor()
        sql = f'SELECT epic_id, epic_display_name FROM players WHERE discord_id = {discord_id}'
        await c.execute(sql)
        res = await c.fetchone()
        account_id = res[0]
        name = res[1]
    else:
        # Get epic_id from display_name
        account_id = await name_to_id(name)
        if account_id == -1:
            return "Couldn't find that name"
    try:

        url = f'https://fn-service-habanero-live-public.ogs.live.on.epicgames.com/api/v1/games/fortnite/trackprogress/{account_id}/byTrack/{season}'
        headers = {
            "Authorization": f"Bearer {TOKEN}"
        }

        res = requests.get(url, headers=headers)
        r = res.json()
        div_id = r['currentDivision']
        div_number = str(100*r['promotionProgress'])+"%"
        divisions = {0: 'Bronze I',
                        1: 'Bronze II',
                        2: 'Bronze III',
                        3: 'Silver I',
                        4: 'Silver II',
                        5: 'Silver III',
                        6: 'Gold I',
                        7: 'Gold II',
                        8: 'Gold III',
                        9: 'Platinum I',
                        10: 'Platinum II',
                        11: 'Platinum III',
                        12: 'Diamond I',
                        13: 'Diamond II',
                        14: 'Diamond III',
                        15: 'Elite',
                        16: 'Champion',
                        17: 'Unreal'}
        div_name = divisions[div_id]
        if div_id == 17:
            div_number = f'#{r['currentPlayerRanking']}'
        response = f"{name}'s rank is: {div_name} {div_number}"
        return response
    except:
        return "Something went wrong"

async def get_user(bot, discord_id):
    c = await bot.db.cursor()
    sql = f'SELECT * FROM players WHERE discord_id = {discord_id}'
    await c.execute(sql)
    user = await c.fetchone()
    return user

async def get_epic_user(bot, epic_id):
    c = await bot.db.cursor()
    sql = f'SELECT * FROM players WHERE epic_id = {epic_id}'
    await c.execute(sql)
    user = await c.fetchone()
    return user

async def register(bot, discord_id, name, user_epic_id):
    c = await bot.db.cursor()
    epic_id = await name_to_id(name)
    if epic_id == -1:
        return "Invalid display name. Please try again and verify"

    # Check if player provided ID matches their display name to validate that they're real
    if user_epic_id and user_epic_id == epic_id:

        #Check if there's already a user registered with that display name and epic_id. Manual conciliation required
        epic_user = get_epic_user(bot, epic_id)
        if epic_user is not None:
            edit(bot, epic_user.discord_id, "", "")

        sql = f"INSERT INTO players (discord_id, epic_display_name, epic_id, revive_rating, validated) VALUES( {int(discord_id)}, '{name}', '{epic_id}', 1000, TRUE)"
    else:
        sql = f"INSERT INTO players (discord_id, epic_display_name, epic_id, revive_rating, validated) VALUES( {int(discord_id)}, '{name}', '{epic_id}', 1000, FALSE)"

    await c.execute(sql)
    await bot.db.commit()
    return "User registered successfully"


async def edit(bot, discord_id, name, epic_id):
    c = await bot.db.cursor()
    edit_fields = ""
    if name:
        edit_fields += f'epic_display_name = {name}'
        if epic_id:
            edit_fields += ", "
    if epic_id:
        user = get_user(bot, discord_id)
        if user.epic_id != epic_id:
            return "Your provided epic ID does not match the display name. Talk to an admin to sort this out"

        edit_fields += f'epic_id = {epic_id}, validated = TRUE'
    sql = f"UPDATE players SET {edit_fields} WHERE discord_id = {int(discord_id)}"
    await c.execute(sql)
    await bot.db.commit()
    return "User edited successfully"


async def add_map(bot, map_code, map_name):
    c = await bot.db.cursor()
    sql = f"INSERT INTO maps (map_code, map_name) values ('{map_code}', '{map_name}')"
    await c.execute(sql)
    await bot.db.commit()
    return "Map Added successfully"


async def remove_map(bot, map_code):
    c = await bot.db.cursor()
    sql = f"DELETE FROM maps WHERE map_code='{map_code}'"
    await c.execute(sql)
    await bot.db.commit()
    return "Map Removed successfully"

async def leaderboard(bot):
    c = await bot.db.cursor()
    sql = f'SELECT epic_display_name, revive_rating FROM players ORDER BY revive_rating DESC'
    await c.execute(sql)
    users = await c.fetchall()

    # Initialize the leaderboard and rank variables
    leaderboard = []
    current_rank = 1
    last_revive_rating = None
    rank_count = 0  # Used to count how many users have the same rating

    for user in users:
        epic_display_name, revive_rating = user

        # If revive_rating is the same as the previous one, increment rank_count
        if revive_rating == last_revive_rating:
            rank_count += 1
        else:
            # Otherwise, reset the rank_count and update the rank
            current_rank += rank_count
            rank_count = 1

        # Add the user to the leaderboard with their current rank
        leaderboard.append((current_rank, epic_display_name, revive_rating))

        # Update last_revive_rating for next iteration
        last_revive_rating = revive_rating

    response = ""
    for rank, epic_display_name, revive_rating in leaderboard:
        response += f'{rank}: {epic_display_name} - Revive Rating: {revive_rating} \n'

    return response

