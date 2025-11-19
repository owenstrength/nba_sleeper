import json
import os
from api.sleeper_api import SleeperAPI
from models.fantasy_data import FantasyData
from simulation.simulation import FantasyNBASimulation
from utils.helpers import (
    get_my_team_and_opponent_team,
    get_player_names_from_team_data,
    get_week_data_filename,
    player_names_to_fantasy_stats,
    get_current_week
)
import time
import questionary


def main():


    # load the player stats from player_info.json if it exists
    player_info = None
    if os.path.exists("player_info.json"):
        print("Loading player info from player_info.json...")
        with open("player_info.json", "r", encoding="utf-8") as f:
            player_info = json.load(f)
    if player_info:
        print(f"Loaded Player Info for user {player_info['username']} (User ID: {player_info['user_id']})")
        print("\n")
    else:
        print("No player info found. Please run setup_player.py first.")
        return
    

    default_week = get_current_week()
    week = questionary.text("Enter the week number:", default=str(default_week)).ask()
    week = int(week)

    roster_id = player_info['roster_id']
    league_id = player_info['main_league_id']



    matchups = SleeperAPI.get_week_matchups(league_id, week)

    user_matchup_data, opp_matchup_data = get_my_team_and_opponent_team(roster_id, matchups)


    my_player_names = get_player_names_from_team_data(user_matchup_data)
    opponent_player_names = get_player_names_from_team_data(opp_matchup_data)

    my_team_fantasy_stats = player_names_to_fantasy_stats(my_player_names)
    opponent_team_fantasy_stats = player_names_to_fantasy_stats(opponent_player_names)

    print("My Team Fantasy Stats:")
    for name, stats in my_team_fantasy_stats.items():
        print(f"{name}: Mean = {stats[0]:.2f}, StdDev = {stats[1]:.2f}, games played = {stats[2]}")

    print("\nOpponent Team Fantasy Stats:")
    for name, stats in opponent_team_fantasy_stats.items():
        print(f"{name}: Mean = {stats[0]:.2f}, StdDev = {stats[1]:.2f}, games played = {stats[2]}")



if __name__ == "__main__":
    main()



