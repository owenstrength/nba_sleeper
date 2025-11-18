import requests
import json

def get_sleeper_players(sport="nba"):
    url = f"https://api.sleeper.app/v1/players/{sport}"
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()

    # Map player_id -> full name
    id_to_name = {
        pid: f"{info.get('first_name', '')} {info.get('last_name', '')}".strip()
        for pid, info in data.items()
        if info.get("first_name") or info.get("last_name")
    }

    return id_to_name

if __name__ == "__main__":
    players = get_sleeper_players("nba")
    print(f"Loaded {len(players)} players.")

    # Save to JSON file
    with open("nba_players.json", "w", encoding="utf-8") as f:
        json.dump(players, f, ensure_ascii=False, indent=2)

    print("Saved to nba_players.json")