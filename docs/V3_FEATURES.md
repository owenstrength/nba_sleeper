# NBA Fantasy Simulator v3.0 - Complete Feature Overview

## 🎉 What's New in v3.0

The app now has a **two-part interface** that separates position management from stats editing, giving you full control over your lineups and player projections.

## 📋 Two-Tab System

### For Each Team (Your Team / Opponent Team):

#### **Tab 1: 📋 Lineup**
Manage your roster positions with an improved interface:

**Features:**
- **Separated Starters & Bench** - Starters shown first, bench players at the bottom
- **Position Labels** - Clear display of each position (PG, SG, G, SF, PF, F, C, UTIL, BN)
- **Dropdown Selectors** - Easy player selection with eligible players only
- **Eligibility Display** - Shows each player's eligible positions next to their name
- **Smart Filtering** - Only players who can fill a position appear in that dropdown
- **Save Button** - Make all changes, then save with one click

**Example Layout:**
```
Starting Lineup:
PG    [Stephen Curry ▼]           Eligible: PG, SG
SG    [Klay Thompson ▼]           Eligible: SG
G     [Luka Doncic ▼]             Eligible: PG, SG
SF    [LeBron James ▼]            Eligible: SF, PF
PF    [Anthony Davis ▼]           Eligible: PF, C
F     [Kevin Durant ▼]            Eligible: SF, PF
C     [Nikola Jokic ▼]            Eligible: C
UTIL  [Damian Lillard ▼]          Eligible: PG, SG
UTIL  [Giannis Antetokounmpo ▼]   Eligible: PF, SF

Bench:
BN    [Bench Player 1 ▼]          Positions: PG
BN    [Bench Player 2 ▼]          Positions: C
BN    [Bench Player 3 ▼]          Positions: SF, PF
BN    [(Empty) ▼]
BN    [(Empty) ▼]
```

#### **Tab 2: 📊 Player Stats**
View and edit all starting players' statistics in a data table:

**Columns:**
- **Player ID** (read-only) - Sleeper player ID
- **Player** (read-only) - Player name
- **Mean** (editable) - Average fantasy points per game
- **Std Dev** (editable) - Standard deviation of fantasy points
- **Games Played** (read-only) - Historical games in dataset
- **Games Left** (editable) - Remaining games this week (0-10)
- **Locked Score** (editable) - Enter locked score or 0 for none

**Use Cases:**
- Adjust projections based on recent performance
- Set games remaining for players who haven't played yet
- Lock in scores for players whose games are complete
- Override historical stats with your own projections

## 🔄 Workflow

### 1. **Load Matchup Data**
```
1. Enter week number
2. Click "Load Matchup Data"
3. App fetches rosters, matchups, and player stats
4. Starting lineup pre-filled based on Sleeper
5. Stats automatically populated from historical data
```

### 2. **Adjust Lineup (Optional)**
```
1. Go to "📋 Lineup" tab
2. Change players using dropdowns
3. Move bench players to starting positions
4. Click "💾 Save Lineup Changes"
5. Stats automatically refresh for new starters
```

### 3. **Edit Stats (Optional)**
```
1. Go to "📊 Player Stats" tab
2. Edit mean, std dev, games left, or locked scores
3. Click "💾 Save Stats Changes"
```

### 4. **Run Simulation**
```
1. Scroll down to "🎲 Run Simulation"
2. Choose number of simulations (default 10,000)
3. Click "🚀 Run Monte Carlo Simulation"
4. View results: win probability, margins, distributions, lock recommendations
```

## ✨ Key Improvements

### **Cleaner Interface**
- Nested tabs organize lineup vs stats
- Less clutter, easier to navigate
- Clear separation of concerns

### **Better Position Management**
- Starters and bench clearly separated
- Eligibility shown inline
- Cleaner dropdown interface (just player names)
- Position info in a separate column

### **Full Stats Visibility**
- See ALL player stats in one table
- Games Played column shows historical data quality
- Mean and Std columns show projection basis
- Edit everything in one place

### **No More Lag**
- Forms prevent constant reruns
- Save buttons batch changes
- Smooth editing experience

### **Auto-Refresh**
- Change lineup → stats auto-refresh
- Always shows stats for current starters
- Preserves manually edited stats (games_left, locked)

## 🎯 Common Tasks

### **Swap a Bench Player into Starting Lineup**
1. Go to "📋 Lineup" tab
2. Find the bench player in a BN slot
3. Note their eligible positions (shown on right)
4. Go to a compatible starting position
5. Select that player from the dropdown
6. Click "💾 Save Lineup Changes"
7. Player stats automatically fetched

### **Lock a Player's Score**
1. Go to "📊 Player Stats" tab
2. Find the player in the table
3. Enter their score in "Locked Score" column
4. Optionally set "Games Left" to 0
5. Click "💾 Save Stats Changes"
6. Run simulation to see updated probabilities

### **Adjust Player Projections**
1. Go to "📊 Player Stats" tab
2. Edit "Mean" to change expected points
3. Edit "Std Dev" to change variability
4. Click "💾 Save Stats Changes"
5. Run simulation with new projections

### **Set Games Remaining**
1. Go to "📊 Player Stats" tab
2. Set "Games Left" for each player
   - 0 = already played all games
   - 1 = one game remaining (default)
   - 2+ = multiple games remaining
3. Click "💾 Save Stats Changes"

## 📊 Data Columns Explained

### **Mean**
- Average fantasy points per game
- Based on historical game logs
- Edit to reflect recent hot/cold streaks

### **Std Dev (Standard Deviation)**
- Measures consistency
- Lower = more predictable
- Higher = more volatile
- Edit for injury concerns or matchup variance

### **Games Played**
- How many games in the historical dataset
- Read-only (shows data quality)
- More games = more reliable mean/std

### **Games Left**
- How many games remaining this week
- Default: 1
- Set to 0 if all games complete
- Set to 2+ for multi-game weeks

### **Locked Score**
- Final score for players whose games are done
- Enter 0 or leave blank for unlocked players
- When locked, "Games Left" is ignored
- Used for mid-week decision making

## 🔍 Technical Details

### Position Eligibility Rules
```python
PG, SG, SF, PF, C → Must have that exact position
G → Can play PG or SG
F → Can play SF or PF
UTIL → Can play any position
BN → Can hold anyone
```

### Stats Refresh Logic
```
Load Matchup → Fetch stats for all starters
Change Lineup → Re-fetch stats for new starters (preserves games_left, locked)
Edit Stats → Save manually entered values
Run Simulation → Uses current stats from session state
```

### Session State
The app maintains:
- `your_roster['lineup']` - Position → Player ID mapping
- `your_player_stats` - Player ID → Stats dict
- `opp_roster['lineup']` - Opponent lineup
- `opp_player_stats` - Opponent stats
- `simulation_results` - Latest simulation output

## 🚀 Performance

- **No lag on editing** - Forms batch all changes
- **Smart caching** - League info cached 1 hour, matchups 5 min
- **Auto-refresh** - Stats update when needed, not on every click
- **Efficient rendering** - Separate tabs prevent full page reruns

## 📝 Tips

1. **Save Often** - Click save buttons after making changes
2. **Check Eligibility** - Look at the right column before moving players
3. **Use Locked Scores** - For mid-week simulations of "what if I lock now?"
4. **Adjust Projections** - Don't trust historical data blindly - edit based on recent trends
5. **Games Left Matters** - A player with 2 games left has 2x the upside (and variance)

## 🔧 Files

- **`app.py`** - Main app (v3.0)
- **`app_v2_backup.py`** - Previous version (backup)
- **`requirements.txt`** - Dependencies
- **`V3_FEATURES.md`** - This file

## 🎬 Getting Started

```bash
streamlit run app.py
```

Then:
1. Complete setup (one-time)
2. Load matchup data for a week
3. Adjust lineup if needed
4. Edit stats if needed
5. Run simulation
6. Review recommendations

Enjoy the enhanced interface!
