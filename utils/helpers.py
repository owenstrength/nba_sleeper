import json
import os
import time
from api.sleeper_api import SleeperAPI
from api.nba_client import NBAApiClient
from models.fantasy_data import FantasyData
from datetime import datetime, date


def get_current_week():
    """Calculate current week number where week 1 started October 20, 2025"""
    week_1_start = date(2025, 10, 20)
    today = date.today()
    
    days_elapsed = (today - week_1_start).days
    current_week = (days_elapsed // 7) + 1
    
    return max(1, current_week)  # Return at least week 1


def get_my_team_and_opponent_team(roster_id, matchups):
    """
    Get your team and opponent team data for a given week and team ID.
    
    Args:
        week (int): The week number
        team_id (int): Your team ID
    
    Returns:
        tuple: (my_team_data, opponent_team_data)
    """
    team_matchup_data = None
    matchup_id = None
    for matchup in matchups:
        if matchup['roster_id'] == roster_id:
            team_matchup_data = matchup
            matchup_id = matchup['matchup_id']
            break
    
    opponent_matchup_data = None
    for matchup in matchups:
        if matchup['matchup_id'] == matchup_id and matchup['roster_id'] != roster_id:
            opponent_matchup_data = matchup
            break

    return team_matchup_data, opponent_matchup_data


def get_player_names_from_team_data(team_data):
    """
    Get player names from team data using sleeper IDs.
    
    Args:
        team_data (dict): Team data containing sleeper IDs
    
    Returns:
        list: List of player names
    """
    player_names = []
    for sleeper_id in team_data['starters']:
        player_name = SleeperAPI.get_name_from_sleeper_id(sleeper_id)
        player_names.append(player_name)
    return player_names


def get_week_data_filename(week):
    """Generate the JSON filename for the given week."""
    return f"week_{week}_fantasy_data.json"


def player_names_to_fantasy_stats(player_names):
    """
    Convert player names to fantasy stats (mean and std).
    
    Args:
        player_names (list): List of player names
    
    Returns:
        dict: Dictionary mapping player names to (mean, std) tuples
    """
    player_fantasy_stats = {}
    for name in player_names:
        try:
            player_id = NBAApiClient.get_player_id_from_name(name)
            time.sleep(0.5)
            game_log = NBAApiClient.get_player_game_log(player_id)
            time.sleep(0.5)
            mean, stddev = FantasyData.get_fantasy_stats(game_log)
            num_games = len(game_log)
            player_fantasy_stats[name] = (mean, stddev, num_games)
        except Exception as e:
            print(f"Error processing player {name}: {e}")
    return player_fantasy_stats


def main():
    print("This is a utility module. Please run the main application.")

if __name__ == "__main__":
    main()