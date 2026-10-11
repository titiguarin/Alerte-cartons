import os, json, requests

API_KEY = os.environ["API_KEY"]
TOKEN = os.environ["TELEGRAM_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]

EUROPE = {
    "England", "Scotland",
    "Spain", "Italy", "Germany", "France", "Netherlands", "Portugal",
    "Belgium", "Turkey", "Switzerland", "Greece"
}

try:
    with open("sent.json") as f:
        sent = set(json.load(f))
except Exception:
    sent = set()

r = requests.get(
    "https://v3.football.api-sports.io/fixtures?live=all",
    headers={"x-apisports-key": API_KEY},
    timeout=30,
)
matches = r.json().get("response", [])

for m in matches:
    league = m["league"]
    name = league["name"]
    european = league["country"] in EUROPE or any(
        k in name for k in ("UEFA", "Champions League", "Europa", "Conference")
    )
    if not european:
        continue
    for e in m.get("events") or []:
        if e["type"] != "Card" or e["detail"] not in ("Red Card", "Second Yellow card"):
            continue
        key = f'{m["fixture"]["id"]}-{e["time"]["elapsed"]}-{e["player"]["id"]}'
        if key in sent:
            continue
        sent.add(key)
        text = (
            f'🟥 Carton rouge !\n'
            f'{m["teams"]["home"]["name"]} {m["goals"]["home"]}-{m["goals"]["away"]} {m["teams"]["away"]["name"]}\n'
            f'{e["player"]["name"]} ({e["team"]["name"]}) à la {e["time"]["elapsed"]}e minute\n'
            f'{name} - {league["country"]}'
        )
        requests.post(
            f"https://api.telegram.org/bot{TOKEN}/sendMessage",
            data={"chat_id": CHAT_ID, "text": text},
            timeout=30,
        )

with open("sent.json", "w") as f:
    json.dump(sorted(sent), f)
