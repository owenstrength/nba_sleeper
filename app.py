import json
import os
import streamlit as st
import numpy as np
import pandas as pd
from api.sleeper_api import SleeperAPI
from utils.helpers import (
    get_my_team_and_opponent_team,
    player_names_to_fantasy_stats,
    get_current_week
)
from simulation.simulation import FantasyNBASimulation

# Page configuration
st.set_page_config(
    page_title="NBA Fantasy Simulator",
    page_icon="🏀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'player_info' not in st.session_state:
    st.session_state.player_info = None
if 'league_info' not in st.session_state:
    st.session_state.league_info = None
if 'your_roster' not in st.session_state:
    st.session_state.your_roster = None
if 'opp_roster' not in st.session_state:
    st.session_state.opp_roster = None
if 'your_player_stats' not in st.session_state:
    st.session_state.your_player_stats = {}
if 'opp_player_stats' not in st.session_state:
    st.session_state.opp_player_stats = {}
if 'simulation_results' not in st.session_state:
    st.session_state.simulation_results = None
if 'week' not in st.session_state:
    st.session_state.week = get_current_week()
if 'players_complete_info' not in st.session_state:
    st.session_state.players_complete_info = None

# Sidebar for navigation
st.sidebar.title("🏀 NBA Fantasy Simulator")
page = st.sidebar.radio("Navigate", ["Setup", "Weekly Simulation"])

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

@st.cache_data
def load_player_info_from_file():
    """Load player info from player_info.json if it exists"""
    if os.path.exists("player_info.json"):
        with open("player_info.json", "r", encoding="utf-8") as f:
            return json.load(f)
    return None

@st.cache_data
def load_players_complete_info():
    """Load complete player information"""
    if os.path.exists("data/json/players_complete_info.json"):
        with open("data/json/players_complete_info.json", "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

@st.cache_data
def load_players_name_map():
    """Load player ID to name mapping"""
    if os.path.exists("data/json/nba_players.json"):
        with open("data/json/nba_players.json", "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_player_info(player_info):
    """Save player info to player_info.json"""
    with open("player_info.json", "w", encoding="utf-8") as f:
        json.dump(player_info, f, indent=2)
    st.session_state.player_info = player_info
    # Clear the cache so the new file contents are loaded
    load_player_info_from_file.clear()

@st.cache_data
def get_user_leagues(user_id):
    """Fetch leagues for a user"""
    return SleeperAPI.get_leagues_for_user(user_id)

@st.cache_data
def get_user_id(username):
    """Get user ID from username"""
    return SleeperAPI.get_user_id_from_username(username)

@st.cache_data
def get_roster_id(league_id, user_id):
    """Get roster ID for a user in a league"""
    return SleeperAPI.get_users_roster_id(league_id, user_id)

@st.cache_data(ttl=300)
def get_rosters(league_id):
    """Get all rosters for a league"""
    return SleeperAPI.get_rosters(league_id)

@st.cache_data(ttl=300)
def get_matchups(league_id, week):
    """Get matchups for a specific week"""
    return SleeperAPI.get_week_matchups(league_id, week)

@st.cache_data(ttl=3600)
def get_league_info(league_id):
    """Get league information including positions and scoring"""
    return SleeperAPI.get_league_info(league_id)

def can_player_fill_position(player_id, position, players_info):
    """Check if a player can fill a specific roster position"""
    if position == "BN":
        return True
    player_info = players_info.get(str(player_id))
    if not player_info:
        return False
    fantasy_positions = player_info.get("fantasy_positions", [])
    if position == "UTIL":
        return len(fantasy_positions) > 0
    elif position == "G":
        return "PG" in fantasy_positions or "SG" in fantasy_positions
    elif position == "F":
        return "SF" in fantasy_positions or "PF" in fantasy_positions
    else:
        return position in fantasy_positions

def get_player_positions(player_id, players_info):
    """Get the fantasy positions a player can play"""
    player_info = players_info.get(str(player_id))
    if player_info:
        return player_info.get("fantasy_positions", [])
    return []

def build_lineup_from_starters_and_bench(starters, all_players, roster_positions, players_info, name_map):
    """Build a lineup dict mapping positions to player IDs"""
    lineup = {i: None for i in range(len(roster_positions))}
    for i, player_id in enumerate(starters):
        if i < len(roster_positions):
            lineup[i] = player_id
    bench_players = [p for p in all_players if p not in starters]
    starter_count = len(starters)
    for i, player_id in enumerate(bench_players):
        position_idx = starter_count + i
        if position_idx < len(roster_positions):
            lineup[position_idx] = player_id
    return lineup

def get_starting_players_from_lineup(lineup, roster_positions):
    """Extract starting players from lineup (non-BN positions)"""
    starters = []
    for i, pos in enumerate(roster_positions):
        if pos != "BN" and lineup.get(i) is not None:
            starters.append(lineup[i])
    return starters

def render_lineup_with_swap(lineup, all_players, roster_positions, players_info, name_map, key_prefix):
    """Render lineup with swap functionality"""

    # Initialize swap selections in session state
    swap_key_1 = f"{key_prefix}_swap_slot_1"
    swap_key_2 = f"{key_prefix}_swap_slot_2"

    if swap_key_1 not in st.session_state:
        st.session_state[swap_key_1] = None
    if swap_key_2 not in st.session_state:
        st.session_state[swap_key_2] = None

    # Create display data
    lineup_display = []
    for i, position in enumerate(roster_positions):
        player_id = lineup.get(i)
        player_name = name_map.get(player_id, "(Empty)") if player_id else "(Empty)"
        positions = get_player_positions(player_id, players_info) if player_id else []

        lineup_display.append({
            "slot": i,
            "position": position,
            "player_id": player_id,
            "player_name": player_name,
            "eligible_positions": ", ".join(positions) if positions else "-"
        })

    # Separate starters and bench
    starters = [item for item in lineup_display if item["position"] != "BN"]
    bench = [item for item in lineup_display if item["position"] == "BN"]

    # Swap interface
    st.write("**🔄 Swap Players** - Select two slots to swap their players")

    col1, col2, col3 = st.columns([2, 2, 1])

    with col1:
        # First slot selector
        slot_options_1 = [f"{item['position']} - {item['player_name']}" for item in lineup_display]
        swap_1_index = st.selectbox(
            "First Slot",
            range(len(slot_options_1)),
            format_func=lambda x: slot_options_1[x],
            key=f"{key_prefix}_swap_select_1"
        )
        st.session_state[swap_key_1] = swap_1_index

    with col2:
        # Second slot selector - filter out slots that can't accept the first slot's player
        first_slot_player_id = lineup_display[swap_1_index]["player_id"]

        # All slots are options for swap
        slot_options_2 = []
        valid_indices_2 = []
        for idx, item in enumerate(lineup_display):
            # Can swap if:
            # 1. Not the same slot
            # 2. First player can fill second position (or first is empty)
            # 3. Second player can fill first position (or second is empty)
            first_pos = lineup_display[swap_1_index]["position"]
            second_pos = item["position"]
            second_player_id = item["player_id"]

            can_swap = True
            if idx == swap_1_index:
                can_swap = False
            elif first_slot_player_id and not can_player_fill_position(first_slot_player_id, second_pos, players_info):
                can_swap = False
            elif second_player_id and not can_player_fill_position(second_player_id, first_pos, players_info):
                can_swap = False

            if can_swap:
                slot_options_2.append(f"{item['position']} - {item['player_name']}")
                valid_indices_2.append(idx)

        if slot_options_2:
            swap_2_index = st.selectbox(
                "Second Slot",
                range(len(slot_options_2)),
                format_func=lambda x: slot_options_2[x],
                key=f"{key_prefix}_swap_select_2"
            )
            st.session_state[swap_key_2] = valid_indices_2[swap_2_index]
        else:
            st.warning("No valid swap targets")
            st.session_state[swap_key_2] = None

    with col3:
        st.write("")  # Spacing
        if st.button("↔️ Swap", key=f"{key_prefix}_swap_btn", type="secondary"):
            if st.session_state[swap_key_1] is not None and st.session_state[swap_key_2] is not None:
                # Perform swap
                slot1 = st.session_state[swap_key_1]
                slot2 = st.session_state[swap_key_2]

                # Swap in lineup
                temp = lineup.get(slot1)
                lineup[slot1] = lineup.get(slot2)
                lineup[slot2] = temp

                st.success(f"✅ Swapped positions!")
                st.rerun()

    st.divider()

    # Display current lineup
    st.write("**📋 Current Lineup**")

    # Starters
    st.write("**Starting:**")
    for item in starters:
        col1, col2, col3 = st.columns([1, 3, 2])
        with col1:
            st.write(f"**{item['position']}**")
        with col2:
            st.write(item['player_name'])
        with col3:
            if item['player_id']:
                st.caption(f"Eligible: {item['eligible_positions']}")

    # Bench
    st.write("**Bench:**")
    for item in bench:
        col1, col2, col3 = st.columns([1, 3, 2])
        with col1:
            st.write(f"**{item['position']}**")
        with col2:
            st.write(item['player_name'])
        with col3:
            if item['player_id']:
                st.caption(f"Positions: {item['eligible_positions']}")

    return lineup

# ============================================================================
# PAGE 1: SETUP
# ============================================================================
if page == "Setup":
    st.title("⚙️ Player Setup")
    st.write("Configure your Sleeper account and select your main league.")

    cached_info = load_player_info_from_file()

    # Add a session state flag to force showing the setup form
    if 'show_setup_form' not in st.session_state:
        st.session_state.show_setup_form = False

    if cached_info and not st.session_state.show_setup_form:
        st.success(f"✅ Found cached player info for **{cached_info.get('username')}**")
        col1, col2 = st.columns(2)
        with col1:
            st.info(f"**User ID:** {cached_info.get('user_id')}")
            st.info(f"**Main League ID:** {cached_info.get('main_league_id')}")
        with col2:
            st.info(f"**Roster ID:** {cached_info.get('roster_id', 'Not set')}")
            st.info(f"**Total Leagues:** {len(cached_info.get('all_leagues', []))}")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("✅ Use This Configuration", type="primary"):
                st.session_state.player_info = cached_info
                st.success("Using cached configuration. Go to **Weekly Simulation** to run analysis.")
                st.rerun()
        with col2:
            if st.button("🔄 Switch to Different User", type="secondary"):
                st.session_state.show_setup_form = True
                st.rerun()

        st.stop()

    # If we're showing the form, allow going back
    if st.session_state.show_setup_form and cached_info:
        if st.button("⬅️ Back to Cached User"):
            st.session_state.show_setup_form = False
            st.rerun()

    st.divider()

    # Initialize session state for setup data
    if 'setup_user_data' not in st.session_state:
        st.session_state.setup_user_data = None

    with st.form("setup_form"):
        st.subheader("Enter Your Sleeper Username")
        username = st.text_input("Sleeper Username", placeholder="YourUsername")
        submit = st.form_submit_button("Fetch User Info", type="primary")

    if submit and username:
        with st.spinner("Fetching user information..."):
            try:
                user_id = get_user_id(username)
                leagues = get_user_leagues(user_id)

                if not leagues:
                    st.error("No leagues found for this user.")
                    st.stop()

                # Store in session state
                st.session_state.setup_user_data = {
                    'username': username,
                    'user_id': user_id,
                    'leagues': leagues
                }

                st.success(f"✅ Found user: **{username}** (ID: {user_id})")

            except Exception as e:
                st.error(f"Error: {str(e)}")
                st.session_state.setup_user_data = None

    # Show league selection if we have user data
    if st.session_state.setup_user_data is not None:
        user_data = st.session_state.setup_user_data

        st.subheader("Select Your Main League")

        league_options = [
            f"{league.get('name', 'Unnamed League')} (ID: {league['league_id']})"
            for league in user_data['leagues']
        ]

        selected_league = st.selectbox(
            "Choose your primary league:",
            options=league_options,
            key="league_select"
        )

        selected_idx = league_options.index(selected_league)
        main_league_id = user_data['leagues'][selected_idx]['league_id']

        if st.button("Confirm League Selection", type="primary", key="confirm_league"):
            with st.spinner("Getting roster information..."):
                try:
                    roster_id = get_roster_id(main_league_id, user_data['user_id'])

                    player_info = {
                        "username": user_data['username'],
                        "user_id": user_data['user_id'],
                        "main_league_id": main_league_id,
                        "roster_id": roster_id,
                        "all_leagues": [league['league_id'] for league in user_data['leagues']]
                    }

                    save_player_info(player_info)

                    # Clear setup data and form flag
                    st.session_state.setup_user_data = None
                    st.session_state.show_setup_form = False

                    st.success("✅ Setup complete! Your configuration has been saved.")
                    st.success(f"**Roster ID:** {roster_id}")
                    st.info("Refreshing page...")

                    st.rerun()

                except Exception as e:
                    st.error(f"Error getting roster: {str(e)}")

# ============================================================================
# PAGE 2: WEEKLY SIMULATION
# ============================================================================
elif page == "Weekly Simulation":
    st.title("📊 Weekly Matchup Simulation")

    if st.session_state.player_info is None:
        cached_info = load_player_info_from_file()
        if cached_info:
            st.session_state.player_info = cached_info
        else:
            st.warning("⚠️ Please complete the **Setup** first.")
            st.stop()

    player_info = st.session_state.player_info

    if st.session_state.league_info is None:
        st.session_state.league_info = get_league_info(player_info['main_league_id'])

    league_info = st.session_state.league_info
    league_name = league_info.get('name', 'Unknown League')
    roster_positions = league_info.get('roster_positions', [])

    if st.session_state.players_complete_info is None:
        st.session_state.players_complete_info = load_players_complete_info()

    players_info = st.session_state.players_complete_info
    name_map = load_players_name_map()

    st.write(f"**League:** {league_name} | **User:** {player_info['username']}")

    # Week selection
    col1, col2 = st.columns([1, 3])
    with col1:
        week = st.number_input(
            "Week Number",
            min_value=1,
            max_value=26,
            value=st.session_state.week,
            step=1,
            key="week_input"
        )

    with col2:
        if st.button("Load Matchup Data", type="primary"):
            st.session_state.week = week
            with st.spinner("Loading matchup data..."):
                try:
                    rosters = get_rosters(player_info['main_league_id'])

                    user_roster = None
                    for roster in rosters:
                        if roster['roster_id'] == player_info['roster_id']:
                            user_roster = roster
                            break

                    if not user_roster:
                        st.error("Could not find your roster")
                        st.stop()

                    matchups = get_matchups(player_info['main_league_id'], week)
                    user_matchup_data, opp_matchup_data = get_my_team_and_opponent_team(
                        player_info['roster_id'],
                        matchups
                    )

                    opp_roster = None
                    for roster in rosters:
                        if roster['roster_id'] == opp_matchup_data['roster_id']:
                            opp_roster = roster
                            break

                    st.session_state.your_roster = {
                        'lineup': build_lineup_from_starters_and_bench(
                            user_matchup_data['starters'],
                            user_roster['players'],
                            roster_positions,
                            players_info,
                            name_map
                        ),
                        'all_players': user_roster['players']
                    }

                    st.session_state.opp_roster = {
                        'lineup': build_lineup_from_starters_and_bench(
                            opp_matchup_data['starters'],
                            opp_roster['players'],
                            roster_positions,
                            players_info,
                            name_map
                        ),
                        'all_players': opp_roster['players']
                    }

                    # Fetch player stats
                    your_starters = get_starting_players_from_lineup(
                        st.session_state.your_roster['lineup'],
                        roster_positions
                    )
                    opp_starters = get_starting_players_from_lineup(
                        st.session_state.opp_roster['lineup'],
                        roster_positions
                    )

                    your_names = [name_map.get(p, 'Unknown') for p in your_starters if p]
                    opp_names = [name_map.get(p, 'Unknown') for p in opp_starters if p]

                    your_stats = player_names_to_fantasy_stats(your_names)
                    opp_stats = player_names_to_fantasy_stats(opp_names)

                    # Build player stats dict
                    st.session_state.your_player_stats = {
                        player_id: {
                            "name": name_map.get(player_id, 'Unknown'),
                            "mean": your_stats.get(name_map.get(player_id, 'Unknown'), (0, 0, 0))[0],
                            "std": your_stats.get(name_map.get(player_id, 'Unknown'), (0, 0, 0))[1],
                            "games_played": your_stats.get(name_map.get(player_id, 'Unknown'), (0, 0, 0))[2],
                            "games_left": 1,
                            "locked": None
                        }
                        for player_id in your_starters if player_id
                    }

                    st.session_state.opp_player_stats = {
                        player_id: {
                            "name": name_map.get(player_id, 'Unknown'),
                            "mean": opp_stats.get(name_map.get(player_id, 'Unknown'), (0, 0, 0))[0],
                            "std": opp_stats.get(name_map.get(player_id, 'Unknown'), (0, 0, 0))[1],
                            "games_played": opp_stats.get(name_map.get(player_id, 'Unknown'), (0, 0, 0))[2],
                            "games_left": 1,
                            "locked": None
                        }
                        for player_id in opp_starters if player_id
                    }

                    st.success(f"✅ Loaded matchup data for Week {week}")

                except Exception as e:
                    st.error(f"Error loading matchup: {str(e)}")
                    import traceback
                    st.code(traceback.format_exc())

    # Display roster editor and stats
    if st.session_state.your_roster is not None and st.session_state.opp_roster is not None:
        st.divider()

        # Tabs for your team vs opponent
        team_tab1, team_tab2 = st.tabs(["🏆 Your Team", "⚔️ Opponent Team"])

        with team_tab1:
            st.subheader("Your Team Management")

            # Sub-tabs for lineup vs stats
            sub_tab1, sub_tab2 = st.tabs(["📋 Lineup", "📊 Player Stats"])

            with sub_tab1:
                st.write("**Manage Positions** - Select players for each position slot")

                your_lineup = st.session_state.your_roster['lineup']
                your_all_players = st.session_state.your_roster['all_players']

                # Use swap interface (no form needed)
                new_your_lineup = render_lineup_with_swap(
                    your_lineup,
                    your_all_players,
                    roster_positions,
                    players_info,
                    name_map,
                    "your"
                )

                # Save button outside the swap function
                if st.button("💾 Save Lineup to Session", key="save_your_lineup", type="primary"):
                    if True:  # Always save when clicked
                        st.session_state.your_roster['lineup'] = new_your_lineup

                        # Refresh stats when lineup changes
                        your_starters = get_starting_players_from_lineup(new_your_lineup, roster_positions)
                        your_names = [name_map.get(p, 'Unknown') for p in your_starters if p]
                        your_stats = player_names_to_fantasy_stats(your_names)

                        st.session_state.your_player_stats = {
                            player_id: {
                                "name": name_map.get(player_id, 'Unknown'),
                                "mean": your_stats.get(name_map.get(player_id, 'Unknown'), (0, 0, 0))[0],
                                "std": your_stats.get(name_map.get(player_id, 'Unknown'), (0, 0, 0))[1],
                                "games_played": your_stats.get(name_map.get(player_id, 'Unknown'), (0, 0, 0))[2],
                                "games_left": st.session_state.your_player_stats.get(player_id, {}).get("games_left", 1),
                                "locked": st.session_state.your_player_stats.get(player_id, {}).get("locked", None)
                            }
                            for player_id in your_starters if player_id
                        }

                        st.success("✅ Lineup saved! Stats refreshed.")
                        st.rerun()

            with sub_tab2:
                st.write("**Edit Player Statistics** - Adjust mean, std, games left, and locked scores")

                if st.session_state.your_player_stats:
                    # Convert to DataFrame
                    stats_data = []
                    for player_id, stats in st.session_state.your_player_stats.items():
                        stats_data.append({
                            "player_id": player_id,
                            "name": stats["name"],
                            "mean": stats["mean"],
                            "std": stats["std"],
                            "games_played": stats["games_played"],
                            "games_left": stats["games_left"],
                            "locked": stats["locked"] if stats["locked"] is not None else 0.0
                        })

                    stats_df = pd.DataFrame(stats_data)

                    with st.form("your_stats_form"):
                        edited_stats_df = st.data_editor(
                            stats_df,
                            column_config={
                                "player_id": st.column_config.TextColumn("ID", disabled=True, width="small"),
                                "name": st.column_config.TextColumn("Player", disabled=True, width="medium"),
                                "mean": st.column_config.NumberColumn("Mean", format="%.2f", width="small"),
                                "std": st.column_config.NumberColumn("Std Dev", format="%.2f", width="small"),
                                "games_played": st.column_config.NumberColumn("Games Played", disabled=True, width="small"),
                                "games_left": st.column_config.NumberColumn("Games Left", min_value=0, max_value=10, width="small"),
                                "locked": st.column_config.NumberColumn("Locked Score (0=None)", format="%.2f", width="small")
                            },
                            hide_index=True,
                            use_container_width=True,
                            key="your_stats_editor"
                        )

                        if st.form_submit_button("💾 Save Stats Changes", type="secondary"):
                            # Update session state
                            for _, row in edited_stats_df.iterrows():
                                player_id = row['player_id']
                                st.session_state.your_player_stats[player_id] = {
                                    "name": row['name'],
                                    "mean": row['mean'],
                                    "std": row['std'],
                                    "games_played": row['games_played'],
                                    "games_left": int(row['games_left']),
                                    "locked": row['locked'] if row['locked'] > 0 else None
                                }
                            st.success("✅ Stats saved!")
                else:
                    st.info("No starters selected yet. Configure lineup first.")

        with team_tab2:
            st.subheader("Opponent Team Management")

            # Sub-tabs for lineup vs stats
            sub_tab1, sub_tab2 = st.tabs(["📋 Lineup", "📊 Player Stats"])

            with sub_tab1:
                st.write("**Manage Positions** - Select players for each position slot")

                opp_lineup = st.session_state.opp_roster['lineup']
                opp_all_players = st.session_state.opp_roster['all_players']

                # Use swap interface (no form needed)
                new_opp_lineup = render_lineup_with_swap(
                    opp_lineup,
                    opp_all_players,
                    roster_positions,
                    players_info,
                    name_map,
                    "opp"
                )

                # Save button outside the swap function
                if st.button("💾 Save Lineup to Session", key="save_opp_lineup", type="primary"):
                    if True:  # Always save when clicked
                        st.session_state.opp_roster['lineup'] = new_opp_lineup

                        # Refresh stats when lineup changes
                        opp_starters = get_starting_players_from_lineup(new_opp_lineup, roster_positions)
                        opp_names = [name_map.get(p, 'Unknown') for p in opp_starters if p]
                        opp_stats = player_names_to_fantasy_stats(opp_names)

                        st.session_state.opp_player_stats = {
                            player_id: {
                                "name": name_map.get(player_id, 'Unknown'),
                                "mean": opp_stats.get(name_map.get(player_id, 'Unknown'), (0, 0, 0))[0],
                                "std": opp_stats.get(name_map.get(player_id, 'Unknown'), (0, 0, 0))[1],
                                "games_played": opp_stats.get(name_map.get(player_id, 'Unknown'), (0, 0, 0))[2],
                                "games_left": st.session_state.opp_player_stats.get(player_id, {}).get("games_left", 1),
                                "locked": st.session_state.opp_player_stats.get(player_id, {}).get("locked", None)
                            }
                            for player_id in opp_starters if player_id
                        }

                        st.success("✅ Lineup saved! Stats refreshed.")
                        st.rerun()

            with sub_tab2:
                st.write("**Edit Player Statistics** - Adjust mean, std, games left, and locked scores")

                if st.session_state.opp_player_stats:
                    # Convert to DataFrame
                    stats_data = []
                    for player_id, stats in st.session_state.opp_player_stats.items():
                        stats_data.append({
                            "player_id": player_id,
                            "name": stats["name"],
                            "mean": stats["mean"],
                            "std": stats["std"],
                            "games_played": stats["games_played"],
                            "games_left": stats["games_left"],
                            "locked": stats["locked"] if stats["locked"] is not None else 0.0
                        })

                    stats_df = pd.DataFrame(stats_data)

                    with st.form("opp_stats_form"):
                        edited_stats_df = st.data_editor(
                            stats_df,
                            column_config={
                                "player_id": st.column_config.TextColumn("ID", disabled=True, width="small"),
                                "name": st.column_config.TextColumn("Player", disabled=True, width="medium"),
                                "mean": st.column_config.NumberColumn("Mean", format="%.2f", width="small"),
                                "std": st.column_config.NumberColumn("Std Dev", format="%.2f", width="small"),
                                "games_played": st.column_config.NumberColumn("Games Played", disabled=True, width="small"),
                                "games_left": st.column_config.NumberColumn("Games Left", min_value=0, max_value=10, width="small"),
                                "locked": st.column_config.NumberColumn("Locked Score (0=None)", format="%.2f", width="small")
                            },
                            hide_index=True,
                            use_container_width=True,
                            key="opp_stats_editor"
                        )

                        if st.form_submit_button("💾 Save Stats Changes", type="secondary"):
                            # Update session state
                            for _, row in edited_stats_df.iterrows():
                                player_id = row['player_id']
                                st.session_state.opp_player_stats[player_id] = {
                                    "name": row['name'],
                                    "mean": row['mean'],
                                    "std": row['std'],
                                    "games_played": row['games_played'],
                                    "games_left": int(row['games_left']),
                                    "locked": row['locked'] if row['locked'] > 0 else None
                                }
                            st.success("✅ Stats saved!")
                else:
                    st.info("No starters selected yet. Configure lineup first.")

        st.divider()

        # Simulation controls
        st.subheader("🎲 Run Simulation")

        col1, col2 = st.columns([1, 3])
        with col1:
            num_sims = st.number_input(
                "Number of Simulations",
                min_value=1000,
                max_value=100000,
                value=10000,
                step=1000
            )

        with col2:
            if st.button("🚀 Run Monte Carlo Simulation", type="primary"):
                with st.spinner(f"Running {num_sims:,} simulations..."):
                    try:
                        # Build player data from stats
                        your_players = [
                            {
                                "name": stats["name"],
                                "mean": stats["mean"],
                                "std": stats["std"],
                                "games_left": stats["games_left"],
                                "locked": stats["locked"]
                            }
                            for stats in st.session_state.your_player_stats.values()
                        ]

                        opp_players = [
                            {
                                "name": stats["name"],
                                "mean": stats["mean"],
                                "std": stats["std"],
                                "games_left": stats["games_left"],
                                "locked": stats["locked"]
                            }
                            for stats in st.session_state.opp_player_stats.values()
                        ]

                        # Run simulation
                        baseline = FantasyNBASimulation.estimate_win_probability(
                            your_players,
                            opp_players,
                            sims=num_sims
                        )

                        # Get lock recommendations
                        recommendations = FantasyNBASimulation.recommend_best_lock(
                            your_players,
                            opp_players,
                            sims=num_sims,
                            min_delta=0.002
                        )

                        st.session_state.simulation_results = {
                            'baseline': baseline,
                            'recommendations': recommendations,
                            'your_players': your_players,
                            'opp_players': opp_players
                        }

                        st.success("✅ Simulation complete!")

                    except Exception as e:
                        st.error(f"Simulation error: {str(e)}")
                        import traceback
                        st.code(traceback.format_exc())

        # Display results
        if st.session_state.simulation_results is not None:
            st.divider()
            st.subheader("📈 Simulation Results")

            results = st.session_state.simulation_results
            baseline = results['baseline']
            recommendations = results['recommendations']

            # Key metrics
            col1, col2, col3 = st.columns(3)

            with col1:
                win_prob = baseline['p_win'] * 100
                st.metric("Win Probability", f"{win_prob:.1f}%")

            with col2:
                expected_margin = baseline['expected_margin']
                st.metric("Expected Margin", f"{expected_margin:.1f} pts")

            with col3:
                your_avg = np.mean(baseline['your_totals'])
                st.metric("Your Avg Score", f"{your_avg:.1f} pts")

            # Distribution visualization
            st.subheader("Score Distribution")
            hist_data = pd.DataFrame({
                'Your Team': baseline['your_totals'],
                'Opponent': baseline['opp_totals']
            })
            st.line_chart(hist_data.sample(min(1000, len(hist_data))))

            # Lock recommendations
            if recommendations['top_recommendation']:
                st.divider()
                st.subheader("🔒 Lock Recommendation")

                top_rec = recommendations['top_recommendation']
                st.success(f"**Recommended Action:** Lock **{top_rec['player_name']}**")

                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Win % if Locked", f"{top_rec['p_win_if_lock'] * 100:.1f}%")
                with col2:
                    st.metric("Win % if Not Locked", f"{top_rec['p_win_if_not_lock'] * 100:.1f}%")
                with col3:
                    delta_pct = top_rec['delta'] * 100
                    st.metric("Improvement", f"+{delta_pct:.2f}%", delta=delta_pct)

                # Show all evaluations
                if recommendations['evaluations']:
                    with st.expander("View All Lock Evaluations"):
                        eval_df = pd.DataFrame(recommendations['evaluations'])
                        eval_df['p_win_if_lock'] = (eval_df['p_win_if_lock'] * 100).round(2)
                        eval_df['p_win_if_not_lock'] = (eval_df['p_win_if_not_lock'] * 100).round(2)
                        eval_df['delta'] = (eval_df['delta'] * 100).round(2)

                        st.dataframe(
                            eval_df[['player_name', 'p_win_if_lock', 'p_win_if_not_lock', 'delta', 'recommended_action']],
                            column_config={
                                "player_name": "Player",
                                "p_win_if_lock": "Win % (Locked)",
                                "p_win_if_not_lock": "Win % (Not Locked)",
                                "delta": "Delta %",
                                "recommended_action": "Action"
                            },
                            hide_index=True,
                            use_container_width=True
                        )
            else:
                st.info("No strong lock recommendations at this time.")

# Footer
st.sidebar.divider()
st.sidebar.caption("NBA Fantasy Simulator v3.0")
st.sidebar.caption("Built with Streamlit")
