# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Purpose

This is a reverse-engineered simulation of the population growth mechanics from **Populous: The Beginning** (Populous 3, Bullfrog/EA 1998). It uses Python's `simpy` discrete-event simulation library to model how AI tribes grow their follower counts, with the goal of accurately replicating in-game constants and breeding formulas.

## Running the Code

Install dependencies (required once):
```bash
pip install simpy matplotlib numpy scikit-learn
```

Run the main simulation:
```bash
python main.py
```

Validate the breeding formula against all measured in-game data:
```bash
python formula_validation.py
```

Compare population-growth strategies (cram vs balanced vs spread):
```bash
python strategy_sim.py
```

Run the working V2 simulation:
```bash
python 123.py
```

There are no tests, linters, or build steps.

## The Breeding Formula (SOLVED)

The formula reproduces all measured in-game times with **no fitted constants** — every number comes straight from the game's `constant.dat` plus the 12.5 game-turns-per-second game speed:

```
T_seconds = (base_sprog_time × band% / 100) / (hut_multiplier × 12.5)
```

- `base_sprog_time` = `{lvl1: 4000, lvl2: 3000, lvl3: 2000}` (P3CONST_HUTn_SPROG_TIME)
- `hut_multiplier` = `0.5 + 0.5 × braves_in_hut` — an **empty hut still breeds** at multiplier 0.5 (confirmed by measurement: lvl 1 empty hut = 197 s vs predicted 192 s)
- `band%` = P3CONST_SPROG%_POP_BAND value, selected by tribe population as a **percentage of the 200 max population** (pop 0–9 → band 00_04 = 30, pop 10–19 → 35, pop 20–29 → 40, …, pop 190+ → 200). Higher population ⇒ **slower** breeding (the band multiplies the time).

Mean error vs. the 15 primary measured data points: **4.6%** (worst 14.3%, on the noisiest small-number measurement). The second measuring session in `formelutregning.py` fits equally well, including the two empty-hut points; its `(3, 2, 14, 19)` row is a recording error (predicted 37 s).

Interpretation: a hut needs `base_sprog_time × band%/100` "sprog points" for a birth and earns `hut_multiplier` points per game turn at 12.5 turns/second.

## Strategy Findings (`strategy_sim.py`)

Total tribe birth rate ∝ `0.5 × (occupied_huts + housed_population)`, so each *additional occupied hut* is worth as much as each *extra brave* — spreading population across many huts beats cramming huts full. With hut build-time cost included, ~2 braves per hut is the sweet spot. Hut level dominates: level 3 huts breed 2× as fast as level 1.

## Architecture

### The Simulation Model (SimPy)

All simulations use `simpy.Environment()` as a discrete-event clock. Entities are Python classes with processes attached via `env.process(...)`. Time advances by `yield env.timeout(n)`. The key loop is:

1. Each `Hut` runs a `breething_process` coroutine that fires on a timer, spawns a new `Brave`, adds it to the hut, and calls `check_hut_full()`
2. When a hut reaches capacity, `split()` creates a new `Hut` with the overflow braves
3. Each homeless `Brave` runs a `create_hut` coroutine that builds a new hut after a random delay
4. `Hut.number_of_huts`, `Brave.number_of_braves`, `Hut.instances`, and `Brave.instances` are class-level counters — they persist across simulation restarts unless explicitly reset

### File Roles

| File | Role |
|---|---|
| `main.py` | Most advanced SimPy version — hut levelling, population bands, graph output |
| `formula_validation.py` | Tests candidate formulas against all measured in-game data; documents the solved formula |
| `strategy_sim.py` | Deterministic event sim comparing hut-allocation strategies (cram/balanced/spread × hut level × build cost) |
| `asd.py` | Simple formula calculator — prints computed vs measured breeding times |
| `123.py` | Working V2 — fixed 97-tick breed rate, huts split at 3 braves |
| `chatGPT4.py` | Alternative implementation — cleaner class design but Braves stop after hut fills |
| `formelutregning.py` | Historical: polynomial regression attempt; its data block doubles as the second measuring session |
| `data fra pop.txt` | Research notes: raw game constants from `constant.dat`, measured in-game timings, formula derivations |
| `graph.py` | Standalone plotter using a hardcoded captured run's population data |

## Known Modelling Quirks in `main.py`

- `hut_upgrade()` adds a free brave on every upgrade and has no level cap (level is capped at lookup time instead)
- Population is not capped at 200, so long runs exceed the real game's maximum
- Class-level `instances` lists and counters (`Brave.number_of_braves`, `Hut.number_of_huts`) are never reset between runs
