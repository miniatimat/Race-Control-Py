import os
from dotenv import load_dotenv
import requests

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

async def get_rank(name,season):
    await get_token()
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
        print(r)
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
        print(response)
        return response
    except:
        return "Something went wrong"
