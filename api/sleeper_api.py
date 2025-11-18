import requests
import json

class SleeperAPI:
    BASE_URL = "https://api.sleeper.app/v1/league/1291191281669644288"

    @staticmethod
    def get_week_matchups(week):
        url = f"{SleeperAPI.BASE_URL}/matchups/{week}"
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Failed to fetch data: {response.status_code}")

    @staticmethod
    def get_my_team_data(data, team_id):
        for matchup in data:
            if matchup['roster_id'] == team_id:
                return matchup
        raise Exception("Team ID not found in the data")

    @staticmethod
    def get_opponent_team_data(data, matchup_id, team_id):
        for matchup in data:
            if matchup['matchup_id'] == matchup_id and matchup['roster_id'] != team_id:
                return matchup
        raise Exception("Opponent team ID not found in the data")
    
    @staticmethod
    def get_name_from_sleeper_id(sleeper_id):
        with open("nba_players.json", "r", encoding="utf-8") as f:
            id_to_name = json.load(f)
        return id_to_name.get(sleeper_id, "Unknown Player")