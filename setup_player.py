import json
import os
from api.sleeper_api import SleeperAPI
from models.fantasy_data import FantasyData
from simulation.simulation import FantasyNBASimulation
from utils.helpers import (
    get_my_team_and_opponent_team,
    get_player_names_from_team_data,
    get_week_data_filename,
    player_names_to_fantasy_stats
)
import questionary

def main():

    load_from_cache = questionary.confirm(
        "Do you want to load player info from cache (player_info.json)?",
        default=True
    ).ask()


    player_info = None
    if os.path.exists("player_info.json"):
        print("Loading player info from player_info.json...")
        with open("player_info.json", "r", encoding="utf-8") as f:
            player_info = json.load(f)

    if player_info and load_from_cache:
        print(f"Loading cached Player Info for user {player_info['username']} (User ID: {player_info['user_id']})")
        print("\n")
    else:
        username = input("Enter your Sleeper username: ").strip()
        user_id = SleeperAPI.get_user_id_from_username(username)
        print(f"Retrieved user ID: {user_id}")
        leagues = SleeperAPI.get_leagues_for_user(user_id)

        for league in leagues:
            print(f"League ID: {league['league_id']}, Name: {league.get('name', 'N/A')}")

        main_league = questionary.select(
            "Select your main league:",
            choices=[f"{league['name']} (ID: {league['league_id']})" for league in leagues]
        ).ask()
        print(f"You selected: {main_league}")

        # Extract the league ID from the selected league
        main_league_id = next(league['league_id'] for league in leagues if f"{league['name']} (ID: {league['league_id']})" == main_league)
        

        player_info = {
            "username": username,
            "user_id": user_id,
            "main_league_id": main_league_id,
            "all_leagues": [league['league_id'] for league in leagues]
        }


    SleeperAPI.DEFAULT_LEAGUE_ID = player_info['main_league_id']
    roster_id = SleeperAPI.get_users_roster_id(player_info['main_league_id'], player_info['user_id'])
    player_info['roster_id'] = roster_id

    with open("player_info.json", "w", encoding="utf-8") as f:
        json.dump(player_info, f, indent=2)

    print(f"Your roster ID in league {player_info['main_league_id']}: {roster_id}")

    # enter the week number
    week = int(input("Enter the week number: "))
    print(f"Using main league ID: {player_info['main_league_id']}")
    weekly_matchups = SleeperAPI.get_week_matchups(week)
    print(f"Weekly Matchups for Week {week}:")

    players_map = json.load(open("nba_players.json", "r", encoding="utf-8"))
    player_team_choices = []
    for matchup in weekly_matchups:
        choice_str = "Team ID " + str(matchup['roster_id'])
        choice_str += " | Players: " + ", ".join([players_map.get(sid, "Unknown Player") for sid in matchup['starters'][:3]])
        player_team_choices.append(choice_str)

    selected_team = questionary.select(
        "Select your team from the weekly matchups:",
        choices=player_team_choices
    ).ask()
    selected_roster_id = int(selected_team.split(" | ")[0].split(" ")[2])
    print(f"You selected roster ID: {selected_roster_id}")

    # your matchup will be the one with the same matchup_id but different roster_id
    opponent = next(
        m for m in weekly_matchups 
        if m['matchup_id'] == next(m2['matchup_id'] for m2 in weekly_matchups if m2['roster_id'] == selected_roster_id) 
        and m['roster_id'] != selected_roster_id
    )
    print(f"Your opponent roster ID: {opponent['roster_id']}")
    # print opponent players
    print("Opponent Players: " + ", ".join([players_map.get(sid, "Unknown Player") for sid in opponent['starters']]))






if __name__ == "__main__":
    main()
    