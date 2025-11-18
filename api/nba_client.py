from nba_api.stats.static import players
from nba_api.stats.endpoints import playergamelog

class NBAApiClient:
    @staticmethod
    def get_player_id_from_name(player_name):
        return players.find_players_by_full_name(player_name)[0]['id']

    @staticmethod
    def get_player_game_log(player_id):
        return playergamelog.PlayerGameLog(player_id=player_id, season="2025-26").get_data_frames()[0]