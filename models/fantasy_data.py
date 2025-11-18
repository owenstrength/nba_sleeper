# given an NBA players name. return their mean and stddev of fantasy points.
# to do this first get the game by game data for that player from the NBA api
# compute fantasy points for each game.
# return mean and stddev of those fantasy points.
# fantasy points are calculated as per standard sleeper scoring rules.
"""
Points = 0.5 point
Rebounds = 1 points
Assists = 1  points
Steals = 2 points
Blocks = 2 points
3_pointer = 0.5 points
double-double = 1 point
triple-double = 2 points
technical fouls = -2 points
flagrant fouls = -2 points
40+ points bonus = 2 points
50+ points bonus = 2 points
Turnovers = -1 point
"""
import numpy as np

class FantasyData:
    @staticmethod
    def calculate_fantasy_points(game_stats):
        if game_stats["MIN"] < 15:
            return -1
        points = game_stats['PTS']
        rebounds = game_stats['REB']
        assists = game_stats['AST']
        steals = game_stats['STL']
        blocks = game_stats['BLK']
        three_pointers = game_stats['FG3M']
        turnovers = game_stats['TOV']
        double_double = 1 if sum([points >= 10, rebounds >= 10, assists >= 10, steals >= 10, blocks >= 10]) >= 2 else 0
        triple_double = 1 if sum([points >= 10, rebounds >= 10, assists >= 10, steals >= 10, blocks >= 10]) >= 3 else 0
        fourty_plus_bonus = 1 if points >= 40 else 0
        fifty_plus_bonus = 1 if points >= 50 else 0

        fantasy_points = (points * 0.5) + (rebounds * 1) + (assists * 1) + (steals * 2)
        + (blocks * 2) + (three_pointers * 0.5) - (turnovers * 1) + (double_double * 1)
        + (triple_double * 2) + (fourty_plus_bonus * 2) + (fifty_plus_bonus * 2)
        return fantasy_points
    
    @staticmethod
    def get_fantasy_stats(player_game_log):
        fantasy_points_list = []
        for _, game in player_game_log.iterrows():
            fantasy_points = FantasyData.calculate_fantasy_points(game)
            if fantasy_points >= 0:
                fantasy_points_list.append(fantasy_points)

        mean_fantasy_points = np.mean(fantasy_points_list)
        stddev_fantasy_points = np.std(fantasy_points_list)

        return mean_fantasy_points, stddev_fantasy_points