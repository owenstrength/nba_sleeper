# NBA Sleeper Fantasy Basketball Optimizer

This project provides tools for analyzing and optimizing your NBA fantasy basketball team on Sleeper, with a focus on the "lock" mechanic decisions.

## Structure

The project is organized into the following directories:

- `api/` - Contains API clients for Sleeper and NBA data
  - `sleeper_api.py` - Interacts with Sleeper API to get matchup data
  - `nba_client.py` - Fetches NBA player statistics
- `data/` - Data processing and management
  - `nba_sleeper_to_name.py` - Maps Sleeper player IDs to names
- `models/` - Fantasy scoring and statistical models
  - `fantasy_data.py` - Calculates fantasy points based on NBA stats
- `simulation/` - Monte Carlo simulation for win probability
  - `simulation.py` - Core simulation engine for lock recommendations
- `main.py` - Main entry point for the application

## Usage

1. **Set up player mapping**:
   ```bash
   python data/nba_sleeper_to_name.py
   ```
   This will download and save the player ID mapping to `nba_players.json`.

2. **Run the analysis**:
   ```bash
   python main.py
   ```
   The script will prompt for a week number and guide you through the analysis process.

## How It Works

1. Fetches your team and opponent's team from Sleeper using the API
2. Retrieves historical NBA stats for each player
3. Calculates mean and standard deviation of fantasy points
4. Allows you to input lock information for players who have already played
5. Runs Monte Carlo simulations to recommend the best player to lock
6. Provides win probability estimates with and without locks

## Dependencies

- `requests` - For API calls
- `numpy` - For numerical computations
- `nba_api` - For NBA statistics
- `scipy` - For statistical functions (optional, in chatgpt.py)

Install dependencies with:
```bash
pip install requests numpy nba-api scipy
```