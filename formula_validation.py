"""
Validates breeding-time formulas against the measured in-game data
from 'data fra pop.txt'.

Models tested:
  A) asd.py        : T = (base / braves) * band%/100
  B) main.py       : T = base * band_factor / (mult * CALIBRATION)
  C) clean model   : T = (base * band%/100) / (mult * TICKRATE)
                     with mult = 0.5 + 0.5*braves  and TICKRATE = 12.5 game
                     turns per second. No fitted constants at all -- every
                     number comes straight from constant.dat plus the 12.5
                     turns/sec game speed.

Measured data: (hut_level, braves_in_hut, population, seconds)
Population bands are % of the 200 max population, so pop 0-9 -> band 00_04 (30),
pop 10-19 -> band 05_09 (35), pop 20-29 -> band 10_14 (40), ...
"""

BASE = {1: 4000, 2: 3000, 3: 2000}
BAND = [30, 35, 40, 50, 60, 70, 80, 90, 100, 110,
        120, 130, 140, 150, 160, 170, 180, 190, 195, 200]
MAX_POP = 200
TICKRATE = 12.5  # game turns per second

# (level, braves, population, measured seconds)
MEASURED = [
    (1, 1, 6, 97), (1, 2, 6, 64), (1, 3, 6, 48),
    (2, 1, 6, 65), (2, 2, 6, 47), (2, 3, 6, 34), (2, 4, 6, 27),
    (3, 1, 6, 48), (3, 2, 6, 30), (3, 3, 6, 22), (3, 4, 6, 18), (3, 5, 6, 14),
    (3, 5, 15, 19),   # "mellom 10-20 pop"
    (3, 5, 25, 22),   # "mellom 20-30 pop"
    (3, 1, 25, 65),   # "mellom 20-30 pop"
]

# Second measuring session, from formelutregning.py. Includes EMPTY huts,
# which constant.dat says breed at multiplier 0.5 ("X 0 - 0.5, ...").
MEASURED_SESSION_2 = [
    (1, 0, 4, 197), (1, 1, 4, 100), (1, 2, 4, 55), (1, 2, 4, 71),
    (1, 1, 14, 116), (1, 3, 14, 57),
    (2, 2, 14, 55), (2, 3, 14, 42), (2, 4, 14, 33),
    (3, 0, 14, 120), (3, 2, 14, 19), (3, 3, 14, 27),
]


def band_pct(population):
    idx = min(int(population / MAX_POP * 100) // 5, 19)
    return BAND[idx]


def mult(braves):
    # constant.dat comment: "X 0 - 0.5, 1 - 1.0, 2 - 1.5, 3 - 2.0 ...."
    return 0.5 + 0.5 * braves


def model_asd(level, braves, population):
    return (BASE[level] / braves) * band_pct(population) / 100


def model_main(level, braves, population):
    # main.py band factors are band% * 0.0916, calibration pins lvl1/1brave to 97
    factor = band_pct(population) * 2.747 / 30
    calibration = BASE[1] * 2.747 / 97
    return BASE[level] * factor / (mult(braves) * calibration)


def model_clean(level, braves, population):
    sprog_points = BASE[level] * band_pct(population) / 100
    return sprog_points / (mult(braves) * TICKRATE)


def report(name, model, data):
    print(f"\n{name}")
    print(f"{'lvl':>3} {'braves':>6} {'pop':>4} {'measured':>9} {'predicted':>9} {'error':>7}")
    errors = []
    for level, braves, pop, sec in data:
        try:
            pred = model(level, braves, pop)
        except ZeroDivisionError:
            print(f"{level:>3} {braves:>6} {pop:>4} {sec:>8}s   (model cannot handle 0 braves)")
            continue
        err = (pred - sec) / sec * 100
        errors.append(abs(err))
        print(f"{level:>3} {braves:>6} {pop:>4} {sec:>8}s {pred:>8.1f}s {err:>+6.1f}%")
    print(f"mean abs error: {sum(errors)/len(errors):.1f}%   worst: {max(errors):.1f}%")


if __name__ == "__main__":
    report("A) asd.py formula  T = base/braves * band%", model_asd, MEASURED)
    report("B) main.py formula (calibrated)", model_main, MEASURED)
    report("C) clean constant.dat model  T = base*band% / (mult * 12.5/s)",
           model_clean, MEASURED)
    report("C on second measuring session (incl. empty huts)",
           model_clean, MEASURED_SESSION_2)
