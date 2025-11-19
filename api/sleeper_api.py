import requests
import json

class SleeperAPI:
    DEFAULT_LEAGUE_ID = "1291191281669644288"
    BASE_URL = f"https://api.sleeper.app/v1/league/{DEFAULT_LEAGUE_ID}"

    @staticmethod
    def get_week_matchups(league_id, week):
        url = f"https://api.sleeper.app/v1/league/{league_id}/matchups/{week}"
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Failed to fetch data: {response.status_code}")

    @staticmethod
    def get_my_team_data(data, roster_id):
        for matchup in data:
            if matchup['roster_id'] == roster_id:
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
    
    @staticmethod
    def get_league_info(league_id):
        url = f"https://api.sleeper.app/v1/league/{league_id}"
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Failed to fetch league info: {response.status_code}")
        
    

    @staticmethod
    def get_rosters(league_id):
        url = f"https://api.sleeper.app/v1/league/{league_id}/rosters"
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Failed to fetch rosters: {response.status_code}")
        
    @staticmethod
    def get_users_roster_id(league_id, user_id):
        url = f"https://api.sleeper.app/v1/league/{league_id}/rosters"
        response = requests.get(url)
        if response.status_code == 200:
            rosters = response.json()
            for roster in rosters:
                if roster['owner_id'] == user_id:
                    return roster['roster_id']
            raise Exception("User ID not found in rosters")
        else:
            raise Exception(f"Failed to fetch rosters: {response.status_code}")
    

    @staticmethod
    def get_user_id_from_username(username):
        url = f"https://api.sleeper.app/v1/user/{username}"
        response = requests.get(url)
        if response.status_code == 200:
            user_data = response.json()
            return user_data['user_id']
        else:
            raise Exception(f"Failed to fetch user ID: {response.status_code}")
        

    @staticmethod
    def get_leagues_for_user(user_id, season="2025"):
        url = f"https://api.sleeper.app/v1/user/{user_id}/leagues/nba/{season}"
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Failed to fetch leagues: {response.status_code}")
        

    @staticmethod
    def get_league_id():
        return SleeperAPI.DEFAULT_LEAGUE_ID
    
    @staticmethod
    def set_league_id(league_id):
        SleeperAPI.DEFAULT_LEAGUE_ID = league_id
        SleeperAPI.BASE_URL = f"https://api.sleeper.app/v1/league/{league_id}"