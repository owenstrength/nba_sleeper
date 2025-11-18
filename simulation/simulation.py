import numpy as np

class FantasyNBASimulation:
    @staticmethod
    def simulate_fantasy_points(mean, stddev, games_left, num_simulations=200, clip_at_zero=True):
        if games_left <= 0:
            return np.zeros(num_simulations)
        
        weekly = np.random.normal(loc=mean, scale=stddev, size=(num_simulations, games_left))
        if clip_at_zero:
            weekly = np.clip(weekly, 0, None)
        totals = weekly.max(axis=1)
        return totals

    @staticmethod
    def get_simulation_statistics(simulated_points):
        mean_simulated = np.mean(simulated_points)
        stddev_simulated = np.std(simulated_points)
        percentile_90 = np.percentile(simulated_points, 90)
        percentile_95 = np.percentile(simulated_points, 95)
        percentile_99 = np.percentile(simulated_points, 99)

        return {
            "mean": mean_simulated,
            "stddev": stddev_simulated,
            "90th_percentile": percentile_90,
            "95th_percentile": percentile_95,
            "99th_percentile": percentile_99
        }

    # ---------------------------
    # Math / notation (short)
    # ---------------------------
    # Let X_ij be fantasy points for player i in game j, with E[X_ij]=mu_i and Var[X_ij]=sigma_i^2.
    # If player i has G_i remaining games, then total for player i:
    #   S_i = sum_{j=1..G_i} X_ij,   E[S_i] = G_i * mu_i,   Var[S_i] = G_i * sigma_i^2  (assuming IID per game)
    # Team total (remaining) = sum_i S_i. If players independent, mean = sum E[S_i], var = sum Var[S_i].
    # Win probability against opponent is P(Team_total + locked_you > Opp_total + locked_opp).
    # We estimate this probability via Monte Carlo by drawing many random totals and counting wins.

    # ---------------------------
    # Team-level simulation
    # ---------------------------
    @staticmethod
    def simulate_team_totals(players, sims=20000):
        sims = sims
        team_total = np.zeros(sims)
        breakdown = {}
        for p in players:
            if p.get("locked") is not None:
                arr = np.full(sims, float(p["locked"]))
            else:
                arr = FantasyNBASimulation.simulate_fantasy_points(
                    mean=p["mean"],
                    stddev=p["std"],
                    games_left=p.get("games_left", 0),
                    num_simulations=sims
                )
            breakdown[p["name"]] = arr
            team_total += arr
        return team_total, breakdown

    # ---------------------------
    # Win probability vs opponent
    # ---------------------------
    @staticmethod
    def estimate_win_probability(your_players, opp_players, sims=20000):
        your_totals, _ = FantasyNBASimulation.simulate_team_totals(your_players, sims=sims)
        opp_totals, _ = FantasyNBASimulation.simulate_team_totals(opp_players, sims=sims)
        p_win = np.mean(your_totals > opp_totals)
        # Also return expected margins
        expected_margin = np.mean(your_totals - opp_totals)
        return {
            "p_win": float(p_win),
            "expected_margin": float(expected_margin),
            "your_totals": your_totals,
            "opp_totals": opp_totals
        }

    # ---------------------------
    # Evaluate locking one player
    # ---------------------------
    @staticmethod
    def evaluate_lock_effect(player_index, your_players, opp_players, sims=20000):
        # Defensive copy
        import copy
        your_copy = copy.deepcopy(your_players)
        opp_copy = copy.deepcopy(opp_players)

        p = your_copy[player_index]
        current_locked_val = p.get("current_live_score", None)
        if current_locked_val is None:
            # nothing to lock (player hasn't played yet) -> no difference
            return {
                "error": "no current_live_score: nothing to lock for this player",
                "recommended_action": "none"
            }

        # branch A: lock this player's current score (replace player's future with locked)
        your_lock = copy.deepcopy(your_copy)
        your_lock[player_index]["locked"] = float(current_locked_val)
        your_lock[player_index].pop("games_left", None)  # no more future games for this slot once locked

        res_lock = FantasyNBASimulation.estimate_win_probability(your_lock, opp_copy, sims=sims)
        p_win_lock = res_lock["p_win"]

        # branch B: do NOT lock -> this player's remaining games simulated normally.
        # If the player also has this game in games_left (i.e., current game is the first of remaining),
        # then leaving unlocked means the current game will be simulated (which matches the live reality)
        # We assume current_live_score is the value you'd lock now, but leaving unlocked keeps the uncertainty.
        res_no_lock = FantasyNBASimulation.estimate_win_probability(your_copy, opp_copy, sims=sims)
        p_win_no_lock = res_no_lock["p_win"]

        delta = p_win_lock - p_win_no_lock

        # Simple decision rule:
        # - if locking increases win prob by > threshold, recommend lock
        # - if decreases by > threshold, recommend wait (i.e., don't lock)
        # threshold can be tuned; we set a small default like 0.005 (0.5% change)
        threshold = 0.005
        if delta > threshold:
            action = "lock"
        elif delta < -threshold:
            action = "wait"
        else:
            action = "indifferent"

        return {
            "p_win_if_lock": float(p_win_lock),
            "p_win_if_not_lock": float(p_win_no_lock),
            "delta_p_win": float(delta),
            "recommended_action": action,
            "details": {
                "res_lock": res_lock,
                "res_no_lock": res_no_lock
            }
        }

    # ---------------------------
    # Batch evaluate all unlockable players and recommend the best one to lock now (if any)
    # ---------------------------
    @staticmethod
    def recommend_best_lock(your_players, opp_players, sims=20000, min_delta=0.001):
        evaluations = []
        for idx, p in enumerate(your_players):
            if p.get("current_live_score") is None:
                continue
            ev = FantasyNBASimulation.evaluate_lock_effect(idx, your_players, opp_players, sims=sims)
            if "error" in ev:
                continue
            ev_summary = {
                "player_index": idx,
                "player_name": your_players[idx]["name"],
                "p_win_if_lock": ev["p_win_if_lock"],
                "p_win_if_not_lock": ev["p_win_if_not_lock"],
                "delta": ev["delta_p_win"],
                "recommended_action": ev["recommended_action"]
            }
            evaluations.append(ev_summary)

        evaluations.sort(key=lambda x: x["delta"], reverse=True)
        top = evaluations[0] if evaluations else None

        if top and top["delta"] >= min_delta and top["recommended_action"] == "lock":
            top_recommendation = top
        else:
            top_recommendation = None

        return {
            "evaluations": evaluations,
            "top_recommendation": top_recommendation
        }

    # ---------------------------
    # Dynamic threshold helper: returns lock/wait thresholds depending on games remaining
    # ---------------------------
    @staticmethod
    def dynamic_risk_threshold(games_remaining, base_upper=0.7, base_lower=0.3):
        # scale factor: more games -> shift thresholds towards 0.5 (more tolerance)
        # use a simple linear interpolation: if games_remaining >= 6 -> shrink gap by 50%
        max_games = 6.0
        frac = min(games_remaining / max_games, 1.0)
        # when frac = 0 (no games left), we want base thresholds (protect more)
        # when frac = 1 (many games), move thresholds towards 0.55/0.45 (more tolerance)
        upper_target = 0.55
        lower_target = 0.45
        upper = base_upper * (1 - frac) + upper_target * frac
        lower = base_lower * (1 - frac) + lower_target * frac
        return upper, lower

# ---------------------------
# Example usage
# ---------------------------
if __name__ == "__main__":
    # Example teams (your team and opponent)
    # For simplicity, mean and std are per GAME
    your_players = [
        {"name": "PG Starter", "mean": 30.0, "std": 8.0, "games_left": 2},        # not played yet
        {"name": "SG Live", "mean": 18.0, "std": 4.0, "games_left": 0,        # already played earlier this week
         "current_live_score": 22.5, "locked": None},                        # you could lock 22.5 now
        {"name": "Bench", "mean": 10.0, "std": 5.0, "games_left": 1},
    ]
    opp_players = [
        {"name": "Opp A", "mean": 25.0, "std": 7.0, "games_left": 2},
        {"name": "Opp B", "mean": 20.0, "std": 5.0, "games_left": 1, "current_live_score": 12.0},
        {"name": "Opp C", "mean": 12.0, "std": 6.0, "games_left": 1},
    ]

    # compute baseline win probability
    baseline = FantasyNBASimulation.estimate_win_probability(your_players, opp_players, sims=10000)
    print(f"Baseline P(win) (no locks applied): {baseline['p_win']:.3f}, expected margin {baseline['expected_margin']:.2f}")

    # Evaluate best lock to make now
    rec = FantasyNBASimulation.recommend_best_lock(your_players, opp_players, sims=10000, min_delta=0.002)
    print("Evaluations (top few):")
    for e in rec["evaluations"][:5]:
        print(e)
    print("Top recommendation:", rec["top_recommendation"])