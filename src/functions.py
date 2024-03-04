import os
from dotenv import load_dotenv
import requests

load_dotenv()
apikey = os.getenv('API_KEY')
headers = {'Authorization':apikey}

async def get_rank(name):
    payload = {'username':name}
    res = requests.get(f'https://fortniteapi.io/v2/ranked/user', headers=headers, params=payload)
    res = res.json()
    rankedData = res["rankedData"]
    for r in rankedData:
        if r["rankingType"] != "delmar-competitive":
            continue
        div_name = r['currentDivision']['name']
        div_number = str(100*r['promotionProgress'])+"%"
        if div_name == "Unreal":
            div_number = f'#{r['currentPlayerRanking']}'
        return f"{name}'s rank is: {div_name} {div_number}"

    return "Something went wrong"
