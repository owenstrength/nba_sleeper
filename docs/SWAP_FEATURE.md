# Swap-Based Lineup Manager 🔄

## Overview

The lineup manager now uses a **swap-based interface** instead of dropdowns. This makes it much easier to move players between positions, especially from bench to starters!

## How It Works

### 🔄 Swap Interface

At the top of the Lineup tab, you'll see:

```
🔄 Swap Players - Select two slots to swap their players

[First Slot ▼]        [Second Slot ▼]        [↔️ Swap]
```

### Step-by-Step

1. **Select First Slot** - Choose the position you want to swap FROM
   - Shows: `PG - Stephen Curry` format
   - Lists all positions (starters + bench)

2. **Select Second Slot** - Choose the position you want to swap TO
   - **Smart filtering** - Only shows valid swap targets!
   - Won't let you make illegal swaps (e.g., can't put a PG-only in a C slot)
   - Automatically excludes the same slot

3. **Click Swap Button** - Instantly swaps the two players
   - Players exchange positions
   - Page refreshes to show updated lineup
   - Can make another swap immediately

### ✅ Swap Validation

The interface **automatically validates** swaps:

- ✅ **Position Eligibility** - Both players must be eligible for their new positions
  - Can swap PG with PG/SG player in G slot ✓
  - Can't swap C with PG in PG slot ✗

- ✅ **Empty Slots** - Can swap with empty slots
  - Swap bench player with empty starter slot ✓
  - Effectively "moves" player to new position

- ✅ **Bench Flexibility** - Bench (BN) accepts anyone
  - Any player can swap into bench ✓
  - Bench players can only go to positions they're eligible for

## Example Workflows

### Move Bench Player to Starting Lineup

**Scenario:** Move "Ja Morant" from bench to PG starter slot

1. **First Slot:** Select `BN - Ja Morant`
2. **Second Slot:** Select `PG - (Empty)` or `PG - Current Player`
3. **Click Swap**
4. Result: Ja Morant now in PG, previous PG player (or empty) on bench

### Swap Two Starters

**Scenario:** Swap positions of two forwards

1. **First Slot:** Select `SF - LeBron James`
2. **Second Slot:** Select `PF - Anthony Davis`
3. **Click Swap**
4. Result: LeBron in PF, Anthony Davis in SF

### Move Starter to Bench

**Scenario:** Bench an injured player

1. **First Slot:** Select `PG - Injured Player`
2. **Second Slot:** Select `BN - (Empty)` (or any bench slot)
3. **Click Swap**
4. Result: Injured player on bench, PG slot empty (or swapped)

### Use Flex Positions (G, F, UTIL)

**Scenario:** Move SG to G slot to open up SG for another player

1. **First Slot:** Select `SG - Devin Booker`
2. **Second Slot:** Select `G - (Empty)`
3. **Click Swap**
4. Result: Booker in G slot, SG slot now open

## Display Format

After the swap interface, you'll see your current lineup:

```
📋 Current Lineup

Starting:
PG    Stephen Curry          Eligible: PG, SG
SG    Klay Thompson          Eligible: SG
G     Luka Doncic            Eligible: PG, SG
SF    LeBron James           Eligible: SF, PF
PF    Anthony Davis          Eligible: PF, C
F     Kevin Durant           Eligible: SF, PF
C     Nikola Jokic           Eligible: C
UTIL  Damian Lillard         Eligible: PG, SG
UTIL  Giannis Antetokounmpo  Eligible: PF, SF

Bench:
BN    Bench Player 1         Positions: PG
BN    Bench Player 2         Positions: C
BN    (Empty)                -
BN    (Empty)                -
BN    (Empty)                -
```

## Smart Validation Examples

### Valid Swaps ✅

| First Slot | Second Slot | Valid? | Why |
|------------|-------------|--------|-----|
| `PG - Curry (PG,SG)` | `G - (Empty)` | ✅ | PG can play G |
| `SF - LeBron (SF,PF)` | `F - (Empty)` | ✅ | SF can play F |
| `PF - Giannis (PF,SF)` | `UTIL - (Empty)` | ✅ | Anyone can play UTIL |
| `C - Jokic (C)` | `BN - (Empty)` | ✅ | Anyone can go to bench |
| `BN - Player (PG)` | `G - (Empty)` | ✅ | PG can play G |

### Invalid Swaps ✗

| First Slot | Second Slot | Valid? | Why |
|------------|-------------|--------|-----|
| `PG - Curry (PG)` | `C - (Empty)` | ✗ | PG can't play C |
| `C - Jokic (C)` | `PG - (Empty)` | ✗ | C can't play PG |
| `SF - LeBron (SF,PF)` | `PG - (Empty)` | ✗ | SF can't play PG |

**Note:** If a swap is invalid, the second slot dropdown simply won't show that option!

## Benefits

### 🎯 **Easier Than Dropdowns**
- No scrolling through long player lists
- See both positions clearly before swapping
- One click to swap instead of two dropdown changes

### 🔒 **Can't Make Mistakes**
- Invalid swaps are prevented automatically
- No more accidentally putting players in illegal positions
- Smart filtering shows only valid options

### ⚡ **Fast Workflow**
- Multiple swaps in succession
- Immediate visual feedback
- No forms to submit between swaps

### 👁️ **Clear Overview**
- See full lineup after swap interface
- Know exactly what changed
- Easy to spot empty slots

## Tips

1. **Bench to Starter:** Always select bench player first, then empty/target starter slot
2. **Empty Slots:** Use swaps with empty slots to "move" rather than "swap"
3. **Flex Positions:** Use G, F, UTIL to maximize lineup flexibility
4. **Multiple Changes:** Make all your swaps, then click "Save Lineup to Session" at bottom
5. **Can't Find Target?** If a slot doesn't appear in second dropdown, the swap isn't valid (check position eligibility)

## Technical Details

### Position Eligibility Logic

```python
# Swap is valid if both these conditions are true:
1. Player A can fill Position B (or Position B is empty)
2. Player B can fill Position A (or Position A is empty)

# Special cases:
- BN (Bench) accepts any player
- UTIL accepts any player
- G accepts PG or SG
- F accepts SF or PF
- Specific positions (PG, SG, SF, PF, C) require exact match
```

### Swap Process

1. User selects first slot → Stored in session state
2. Second dropdown filters based on first selection
3. User clicks "Swap" button
4. Positions exchanged in lineup dict
5. Page reruns with updated lineup
6. Can make another swap immediately

### Saving

- Swaps update the session state lineup immediately (via `st.rerun()`)
- Click "💾 Save Lineup to Session" to persist and fetch new player stats
- Stats refresh happens when you save, not on every swap

## Comparison: Old vs New

### Old (Dropdown) Interface
```
PG    [Stephen Curry ▼ Select from 15 players...]
SG    [Klay Thompson ▼ Select from 12 players...]
...
BN    [Bench Player 1 ▼ Select from 15 players...]
```

**Issues:**
- Long dropdown lists
- Hard to find players
- Two changes needed to swap
- Can accidentally pick wrong player

### New (Swap) Interface
```
🔄 Swap Players
First Slot:  [PG - Stephen Curry ▼]
Second Slot: [BN - Ja Morant ▼]
[↔️ Swap]
```

**Benefits:**
- See both slots clearly
- One action to swap
- Filtered valid targets only
- Visual confirmation

## Future Enhancements

Potential improvements:
- Visual drag-and-drop (requires custom Streamlit component)
- Quick swap buttons next to each player
- "Optimize Lineup" auto-fill feature
- Highlight illegal positions in red

For now, the swap interface provides the best balance of functionality and simplicity within Streamlit's native capabilities!
