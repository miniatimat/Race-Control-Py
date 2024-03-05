import os
from dotenv import load_dotenv
import requests

load_dotenv()
DEVICE = os.getenv('DEVICE_ID'),
ACCOUNT= os.getenv('ACCOUNT_ID'),
SECRET = os.getenv('ACCOUNT_SECRET')

async def get_token():
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
    print(res)
    return res['access_token']

async def get_rank(name):
    url = f'https://fn-service-habanero-live-public.ogs.live.on.epicgames.com/api/v1/games/fortnite/trackprogress/{ACCOUNT}'
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Authorization": f"Bearer {await get_token()}"
    }

    res = requests.get(url, headers=headers)
    res = res.json()
    for r in res:
        if r["rankingType"] != "delmar-competitive":
            continue
        print(r)
        div_id = r['currentDivision']
        div_number = str(100*r['promotionProgress'])+"%"
        match div_id:
            case 0:
                div_name = "Bronze 1"
            case 1:
                div_name = "Bronze 2"
            case 2:
                div_name = "Bronze 3"
            case 3:
                div_name = "Silver 1"
            case 4:
                div_name = "Silver 2"
            case 5:
                div_name = "Silver 3"
            case 6:
                div_name = "Gold 1"
            case 7:
                div_name = "Gold 2"
            case 8:
                div_name = "Gold 3"
            case 9:
                div_name = "Platinum 1"
            case 10:
                div_name = "Platinum 2"
            case 11:
                div_name = "Platinum 3"
            case 12:
                div_name = "Diamond 1"
            case 13:
                div_name = "Diamond 2"
            case 14:
                div_name = "Diamond 3"
            case 15:
                div_name = "Elite"
            case 16:
                div_name = "Champion"
            case 17:
                div_name = "Unreal"
                div_number = f'#{r['currentPlayerRanking']}'
            case _:
                div_name = "Unranked"
                div_number = ""

        return f"{name}'s rank is: {div_name} {div_number}"

    return "Something went wrong"
