# Position Management Features - v2.0

## What's New

The Streamlit app now includes full position management, allowing you to:
- View and edit lineups with proper position constraints
- Move players between starting positions and bench
- See bench players and swap them in
- Position eligibility validation (PG, SG, G, SF, PF, F, C, UTIL, BN)

## Key Features

### 1. **Position-Aware Roster Loading**
- Automatically loads your league's roster positions from Sleeper
- Shows league name at the top
- Displays positions like: `['PG', 'SG', 'G', 'SF', 'PF', 'F', 'C', 'UTIL', 'UTIL', 'BN', 'BN', 'BN', 'BN', 'BN']`

### 2. **Lineup Editor**
Each position slot shows:
- **Position label** (e.g., PG, SG, F, UTIL, BN)
- **Dropdown selector** with eligible players only
- **Player's eligible positions** in parentheses (e.g., "LeBron James (SF, PF)")

### 3. **Position Eligibility Rules**
The app automatically filters players based on position eligibility:
- **PG, SG, SF, PF, C**: Only players with that specific position
- **G**: Can play PG or SG
- **F**: Can play SF or PF
- **UTIL**: Can play any position
- **BN** (Bench): Can hold any player

### 4. **Player Complete Info Integration**
Uses `data/json/players_complete_info.json` to determine:
- Player's available fantasy positions
- Full player metadata

## How to Use

### Setting Up Your Lineup

1. **Load Matchup Data** for your desired week
2. You'll see two tabs: "Your Team" and "Opponent Team"
3. Each tab shows a form with position slots

### Editing Positions

1. For each position slot, you'll see a dropdown
2. Only **eligible players** for that position are shown
3. Select a player from the dropdown
4. You can move bench players into starting positions
5. Click **"💾 Save Your Lineup"** to commit changes

### Example Workflow

```
PG    [Dropdown: Stephen Curry (PG, SG)]
SG    [Dropdown: Klay Thompson (SG)]
G     [Dropdown: Luka Doncic (PG, SG)]  ← Can play PG or SG
SF    [Dropdown: LeBron James (SF, PF)]
PF    [Dropdown: Anthony Davis (PF, C)]
F     [Dropdown: Kevin Durant (SF, PF)]  ← Can play SF or PF
C     [Dropdown: Nikola Jokic (C)]
UTIL  [Dropdown: Damian Lillard (PG, SG)]  ← Can play any position
UTIL  [Dropdown: (Empty)]
BN    [Dropdown: Bench Player 1 (PG)]
BN    [Dropdown: Bench Player 2 (C)]
...
```

### Moving Players from Bench to Starting

1. Find the bench player in a **BN** position slot
2. Note their eligible positions (shown in parentheses)
3. Go to a compatible position slot (e.g., if player is PG, you can put them in PG, G, or UTIL)
4. Select that player from the dropdown
5. The bench slot will show "(Empty)" or you can select another bench player
6. Click **"Save Your Lineup"**

## Data Flow

1. **Load Matchup Data** →
   - Fetches rosters (includes all players + bench)
   - Fetches matchups (includes current starters)
   - Builds lineup from starters + remaining players go to bench slots

2. **Edit Lineup** →
   - Change dropdown selections
   - Validation ensures only eligible players can fill each position
   - Click save to update session state

3. **Run Simulation** →
   - Extracts starting players (non-BN positions) from lineup
   - Fetches their stats
   - Runs Monte Carlo simulation

## Technical Details

### Position Validation Logic

```python
def can_player_fill_position(player_id, position, players_info):
    """
    PG, SG, SF, PF, C → Must have exact position
    G → Must have PG or SG
    F → Must have SF or PF
    UTIL → Can have any position
    BN → Can be anyone
    """
```

### Data Sources

- **`data/json/players_complete_info.json`**: Player fantasy positions (`fantasy_positions` field)
- **`data/json/nba_players.json`**: Player ID to name mapping
- **League Info API**: Roster positions and scoring settings
- **Rosters API**: All players on each team (including bench)
- **Matchups API**: Current starters for the week

## Scoring Settings (Future Enhancement)

The app currently loads league scoring settings but doesn't use them yet. Future versions will:
- Calculate fantasy points based on your league's custom scoring
- Show projected points using league-specific weights
- Support custom scoring systems

Your league's scoring settings are available in session state:
```python
st.session_state.league_info['scoring_settings']
# Example: {'pts': 0.5, 'reb': 1.0, 'ast': 1.0, 'stl': 2.0, 'blk': 2.0, ...}
```

## Benefits

✅ **See Your Full Roster**: Not just starters, but bench players too
✅ **Easy Swaps**: Move players between positions with dropdowns
✅ **Validation**: Can't put a PG in a C slot (unless it's UTIL)
✅ **Position Flexibility**: Understand which players can play multiple positions
✅ **Realistic Lineups**: Matches exactly how Sleeper positions work
✅ **Both Teams**: Can edit opponent lineup to simulate different scenarios

## Troubleshooting

**Q: I don't see my bench players**
A: Make sure you clicked "Load Matchup Data". Bench players are in the BN position slots at the bottom.

**Q: A player doesn't show up in a dropdown**
A: That player isn't eligible for that position. Check their positions in parentheses and select them for a compatible slot.

**Q: Changes aren't saved**
A: Make sure to click "💾 Save Your Lineup" after making changes. The form prevents auto-saving to avoid lag.

**Q: Player positions seem wrong**
A: Player positions come from Sleeper's API (`data/json/players_complete_info.json`). If they're incorrect, Sleeper may need to update them.
