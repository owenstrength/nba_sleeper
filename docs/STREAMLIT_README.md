# NBA Fantasy Simulator - Streamlit App

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run the Streamlit App

```bash
streamlit run app.py
```

This will open the app in your browser at `http://localhost:8501`

## How to Use

### Setup Page
1. Enter your Sleeper username
2. Click "Fetch User Info"
3. Select your main league from the dropdown
4. Click "Confirm League Selection"

Your configuration will be saved to `player_info.json` for future use.

### Weekly Simulation Page
1. Enter the week number you want to analyze
2. Click "Load Matchup Data" to fetch your matchup
3. Review and edit player stats in the tables:
   - Adjust "Games Left" for players who haven't played yet
   - Enter "Locked Score" for players whose games are complete
4. Click "Run Monte Carlo Simulation"
5. View results:
   - Win probability
   - Expected margin
   - Score distributions
   - Lock recommendations

## Features

- **Interactive Tables**: Edit player stats directly in the browser
- **Visual Results**: Charts showing score distributions
- **Lock Recommendations**: Get data-driven suggestions on which players to lock
- **Caching**: Fast API responses using Streamlit's caching
- **Session State**: Your data persists as you navigate between pages

## Tips

- Use the sidebar to navigate between Setup and Weekly Simulation
- Player info is cached, so you only need to set up once
- You can run multiple simulations with different parameters
- Lock recommendations are based on Monte Carlo analysis (default: 10,000 simulations)

## Comparison with CLI Tools

The Streamlit app replaces manual input with:
- Forms and text inputs instead of `input()` prompts
- Interactive tables instead of manual data entry
- Visual charts instead of text output
- Real-time updates instead of sequential execution

You can still use the original CLI tools (`setup_player.py`, `get_weekly_stats.py`, `main.py`) if preferred.
