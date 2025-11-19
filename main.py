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

def main():
    week = int(input("Enter the week number: "))
    team_id = int(input("Enter your team ID: "))
    filename = get_week_data_filename(week)

    username = input("Enter your Sleeper username: ").strip()
    user_id = SleeperAPI.get_user_id_from_username(username)

    print(f"Retrieved user ID: {user_id}")

    leagues = SleeperAPI.get_leagues_for_user(user_id)
    print("Leagues for user:")
    print(json.dumps(leagues, indent=2))
    print("\n")
    
    # Check if the JSON file for this week already exists
    if os.path.exists(filename):
        print(f"Loading data from {filename}...")
        with open(filename, 'r') as f:
            week_data = json.load(f)
        
        my_team_fantasy_stats = {p['name']: (p['mean'], p['std']) for p in week_data['your_players']}
        opponent_team_fantasy_stats = {p['name']: (p['mean'], p['std']) for p in week_data['opp_players']}
        
        # Use the saved player data
        my_player_names = [p['name'] for p in week_data['your_players']]
        opponent_player_names = [p['name'] for p in week_data['opp_players']]
        
        your_players = week_data['your_players']
        opp_players = week_data['opp_players']
    else:
        print(f"No data file found for week {week}. Creating new data...")
        
        my_team_data, opponent_team_data = get_my_team_and_opponent_team(week, team_id)

        my_player_names = get_player_names_from_team_data(my_team_data)
        opponent_player_names = get_player_names_from_team_data(opponent_team_data)

        my_team_fantasy_stats = player_names_to_fantasy_stats(my_player_names)
        opponent_team_fantasy_stats = player_names_to_fantasy_stats(opponent_player_names)

        print("My Team Fantasy Stats:")
        for name, stats in my_team_fantasy_stats.items():
            print(f"{name}: Mean = {stats[0]:.2f}, StdDev = {stats[1]:.2f}")

        print("\nOpponent Team Fantasy Stats:")
        for name, stats in opponent_team_fantasy_stats.items():
            print(f"{name}: Mean = {stats[0]:.2f}, StdDev = {stats[1]:.2f}")

        def ask_player_meta(name, stats_dict):
            mean_std = stats_dict.get(name)
            if not mean_std:
                print(f"Warning: no historical stats for {name}. Please enter manually.")
                mean = float(input(f"  mean for {name}: ").strip())
                std = float(input(f"  stddev for {name}: ").strip())
            else:
                mean, std = mean_std

            locked_score = None
            games_left = None
            if input(f"Has {name} been LOCKED? (y/N): ").strip().lower().startswith("y"):
                locked_score = float(input(f"  Enter locked score for {name}: ").strip())
            else:
                games_left_raw = input(f"How many games left for {name}? [default 1]: ").strip()
                games_left = int(games_left_raw) if games_left_raw else 1

            return {
                "name": name,
                "mean": mean,
                "std": std,
                "games_left": games_left,
                "locked": locked_score,
            }

        your_players = [ask_player_meta(n, my_team_fantasy_stats) for n in my_player_names]
        opp_players = [ask_player_meta(n, opponent_team_fantasy_stats) for n in opponent_player_names]
        
        week_data = {
            "your_players": your_players,
            "opp_players": opp_players
        }
        with open(filename, 'w') as f:
            json.dump(week_data, f, indent=2)
        print(f"Data saved to {filename}")
    
    if os.path.exists(filename):
        print("Data loaded from file. Do you want to update any player information?")
        update_choice = input("Enter 'y' to update player info, or press Enter to continue with existing data: ").strip().lower()
        
        if update_choice.startswith('y'):
            def update_player_meta(player):
                name = player['name']
                mean = player['mean']
                std = player['std']
                
                print(f"\nCurrent info for {name}: Mean = {mean:.2f}, Std = {std:.2f}, Locked = {player['locked']}, Games left = {player['games_left']}")
                
                # Ask if they want to update mean/std
                if input(f"Update mean/std for {name}? (y/N): ").strip().lower().startswith("y"):
                    mean = float(input(f"  New mean for {name}: ").strip())
                    std = float(input(f"  New stddev for {name}: ").strip())
                
                # Ask about lock status
                if player['locked'] is not None:
                    if input(f"{name} is currently LOCKED with score {player['locked']}. Update? (Y/n): ").strip().lower() != "n":
                        if input(f"Keep {name} LOCKED? (Y/n): ").strip().lower() != "n":
                            locked_score = float(input(f"  Enter new locked score for {name}: ").strip())
                        else:
                            locked_score = None
                            games_left_raw = input(f"How many games left for {name}? [default {player['games_left']}]: ").strip()
                            games_left = int(games_left_raw) if games_left_raw else player['games_left']
                    else:
                        locked_score = player['locked']
                        games_left = player['games_left']
                else:
                    if input(f"Has {name} been LOCKED? (y/N): ").strip().lower().startswith("y"):
                        locked_score = float(input(f"  Enter locked score for {name}: ").strip())
                        games_left = 0  # Set to 0 when locked
                    else:
                        games_left_raw = input(f"How many games left for {name}? [default {player['games_left']}]: ").strip()
                        games_left = int(games_left_raw) if games_left_raw else player['games_left']
                
                return {
                    "name": name,
                    "mean": mean,
                    "std": std,
                    "games_left": games_left,
                    "locked": locked_score,
                }
            
            your_players = [update_player_meta(p) for p in week_data['your_players']]
            opp_players = [update_player_meta(p) for p in week_data['opp_players']]
            
            # Save updated data back to the JSON file
            week_data = {
                "your_players": your_players,
                "opp_players": opp_players
            }
            with open(filename, 'w') as f:
                json.dump(week_data, f, indent=2)
            print(f"Updated data saved to {filename}")

    baseline = FantasyNBASimulation.estimate_win_probability(your_players, opp_players, sims=10000)
    print(f"\nBaseline P(win) (no locks applied): {baseline['p_win']:.3f}, expected margin {baseline['expected_margin']:.2f}")

    rec = FantasyNBASimulation.recommend_best_lock(your_players, opp_players, sims=10000, min_delta=0.002)
    print("\nEvaluations (top few):")
    for e in rec.get("evaluations", [])[:5]:
        print(e)
    print("Top recommendation:", rec.get("top_recommendation"))

if __name__ == "__main__":
    main()