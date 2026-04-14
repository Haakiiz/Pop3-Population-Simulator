# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Purpose

This is a reverse-engineered simulation of the population growth mechanics from **Populous: The Beginning** (Populous 3, Bullfrog/EA 1998). It uses Python's `simpy` discrete-event simulation library to model how AI tribes grow their follower counts, with the goal of accurately replicating in-game constants and breeding formulas.

## Running the Code

Install dependencies (required once):
```bash
pip install simpy matplotlib numpy scikit-learn
```

Run the main simulation (currently has a bug — see below):
```bash
python main.py
```

Run the working V2 simulation:
```bash
python 123.py
```

Test the breeding formula calculator:
```bash
python asd.py
```

Run the polynomial regression formula finder:
```bash
python formelutregning.py
```

There are no tests, linters, or build steps.

## Architecture

### The Simulation Model (SimPy)

All simulations use `simpy.Environment()` as a discrete-event clock. Entities are Python classes with processes attached via `env.process(...)`. Time advances by `yield env.timeout(n)`. The key loop is:

1. Each `Hut` runs a `breething_process` coroutine that fires on a timer, spawns a new `Brave`, adds it to the hut, and calls `check_hut_full()`
2. When a hut reaches capacity, `split()` creates a new `Hut` with the overflow braves
3. Each homeless `Brave` runs a `create_hut` coroutine that builds a new hut after a random delay
4. `Hut.number_of_huts`, `Brave.number_of_braves`, `Hut.instances`, and `Brave.instances` are class-level counters — they persist across simulation restarts unless explicitly reset

### Game Mechanics Being Modelled

The breeding time formula uses three factors:
- **Hut level** (1–3): `base_sprog_time = {1: 4000, 2: 3000, 3: 2000}`
- **Braves in hut**: `hut_multiplier = {0:0, 1:1, 2:1.5, 3:2, 4:2.5, 5:3}` — more braves = faster
- **Population band**: `population_band_factors` — larger tribe population = faster breeding, based on real values from the game's `constant.dat`

Target breeding times (measured from actual gameplay, in `data fra pop.txt`):
- lvl 1 hut, 1 brave, pop <9 → 97 ticks
- lvl 1 hut, 2 braves → 64 ticks
- lvl 3 hut, 5 braves → 14 ticks

### File Roles

| File | Role |
|---|---|
| `main.py` | Most advanced version — hut levelling, population bands, graph output. **Has a bug (see below)** |
| `123.py` | Working V2 — fixed 97-tick breed rate, huts split at 3 braves |
| `chatGPT4.py` | Alternative implementation — cleaner class design but Braves stop after hut fills |
| `asd.py` | Formula tester — prints computed vs expected breeding times |
| `formelutregning.py` | Polynomial regression (sklearn) to reverse-engineer the formula from measured data |
| `data fra pop.txt` | Research notes: raw game constants from `constant.dat`, measured in-game timings, formula derivations |
| `graph.py` | Standalone plotter using a hardcoded captured run's population data |

## Known Bugs in `main.py`

**Critical — crashes immediately:**  
`find_breething_duration()` at line 88 multiplies `hut_multiplier` (a dict) by an int:
```python
breething_duration = (base_sprog_time / (hut_multiplier * braves_antall * population_band))
```
Should index the dict: `hut_multiplier[self.level]` — but `self.level` is not passed into the function.

**Secondary issues:**
- `hut_upgrade()` increments `self.level` without a cap, but `base_sprog_time` only has keys 1–3 (will `KeyError` at level 4)
- `graph_maker` references `Brave` before it is defined when `Tribe.__init__` runs at module level
- Class-level `instances` lists and counters (`Brave.number_of_braves`, `Hut.number_of_huts`) are never reset between runs

## The Formula Problem

`asd.py` outputs are wrong — e.g., `breeding_time(1, 1, 4)` returns `1200` but the target is `97`. The formula `(base_sprog_time / hut_multiplier) * population_band_modifier` does not match the actual game behaviour. `formelutregning.py` exists specifically to find a better formula via regression. The correct formula has not yet been nailed down and is the core open problem in this project.
