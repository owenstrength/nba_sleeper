from nba_api.stats.static import players
from nba_api.stats.endpoints import playergamelog
import re

class NBAApiClient:
    @staticmethod
    def get_player_id_from_name(player_name):
        # Make pattern case-insensitive and allow partial matches
        pattern = ".*".join(re.escape(word) for word in player_name.split())
        results = players.find_players_by_full_name(pattern)
        
        if results:
            return results[0]['id']
        else:
            raise ValueError(f"No match found for: {player_name}")
    @staticmethod
    def get_player_game_log(player_id):
        return playergamelog.PlayerGameLog(player_id=player_id, season="2025-26").get_data_frames()[0]