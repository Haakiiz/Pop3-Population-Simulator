"""
Strategy comparison: what is the fastest way to grow tribe population?

Uses the validated breeding formula (see formula_validation.py):

    T_seconds = (base_sprog_time * band% / 100) / ((0.5 + 0.5*braves) * 12.5)

Key consequence of the formula: a hut's breed-rate is proportional to
0.5 + 0.5*braves.  Summed over all huts the tribe's total birth rate is

    rate  ~  0.5 * (occupied_huts + housed_braves)

so every *occupied hut* adds as much as every *extra brave* in a hut.
The strategies below test how to allocate braves to huts:

  cram    -- minimum huts: only build a new hut when every hut is full
  spread  -- maximum huts: every brave gets their own hut
  balanced-- keep 2 braves per hut before building new huts

Each strategy is run with all-level-1 huts and all-level-3 huts, and with a
configurable hut build cost (the builder is out of the breeding pool while
building).  Deterministic event simulation, no randomness.
"""

import heapq

BASE = {1: 4000, 2: 3000, 3: 2000}
CAPACITY = {1: 3, 2: 4, 3: 5}
BAND = [30, 35, 40, 50, 60, 70, 80, 90, 100, 110,
        120, 130, 140, 150, 160, 170, 180, 190, 195, 200]
MAX_POP = 200
TICKRATE = 12.5


def band_pct(population):
    idx = min(int(population / MAX_POP * 100) // 5, 19)
    return BAND[idx]


def breed_time(level, braves, population):
    if braves == 0:
        return None
    mult = 0.5 + 0.5 * braves
    return (BASE[level] * band_pct(population) / 100) / (mult * TICKRATE)


class Sim:
    """Event-driven sim. Huts hold braves; a hut with b braves produces a
    birth every breed_time(level, b, pop) seconds. New braves are placed by
    the strategy; placing into a new hut costs build_time seconds during
    which the brave is housed nowhere."""

    def __init__(self, strategy, level, build_time=0.0, start_braves=6,
                 target=190):
        self.strategy = strategy
        self.level = level
        self.build_time = build_time
        self.target = target
        self.pop = 0
        self.huts = []            # list of brave-counts per hut
        self.now = 0.0
        self.events = []          # (time, seq, kind, hut_index)
        self.seq = 0
        self.milestones = {}
        for _ in range(start_braves):
            self.place_new_brave()

    def push(self, dt, kind, hut):
        self.seq += 1
        heapq.heappush(self.events, (self.now + dt, self.seq, kind, hut))

    def schedule_breed(self, hut):
        t = breed_time(self.level, self.huts[hut], self.pop)
        if t is not None:
            self.push(t, ('breed', self.huts[hut]), hut)

    def place_new_brave(self):
        self.pop += 1
        hut = self.strategy(self.huts, CAPACITY[self.level])
        if hut is None:                       # build a new hut
            if self.build_time > 0:
                self.push(self.build_time, ('built', None), None)
            else:
                self.finish_hut()
        else:
            self.huts[hut] += 1
            self.schedule_breed(hut)          # occupancy changed -> new timer

    def finish_hut(self):
        self.huts.append(1)
        self.schedule_breed(len(self.huts) - 1)

    def run(self, until=36000):
        check = sorted(set(range(25, self.target, 25)) | {self.target})
        while self.events and self.pop < self.target and self.now < until:
            self.now, _, kind, hut = heapq.heappop(self.events)
            tag, detail = kind
            if tag == 'built':
                self.finish_hut()
                continue
            # stale timer: hut occupancy changed since this was scheduled
            if detail != self.huts[hut]:
                continue
            self.place_new_brave()
            self.schedule_breed(hut)          # parent hut breeds again
            while check and self.pop >= check[0]:
                self.milestones[check.pop(0)] = self.now
        return self


def cram(huts, cap):
    """Fill existing huts to the brim before building."""
    fullest = None
    for i, b in enumerate(huts):
        if b < cap and (fullest is None or b > huts[fullest]):
            fullest = i
    return fullest          # None -> all full -> build


def spread(huts, cap):
    """Always build a new hut for every brave."""
    return None


def balanced(huts, cap):
    """Top huts up to 2 braves, then build."""
    for i, b in enumerate(huts):
        if b < 2:
            return i
    return None


if __name__ == "__main__":
    scenarios = [
        ("cram", cram), ("balanced", balanced), ("spread", spread),
    ]
    for build_time in (0, 60, 120):
        print(f"\n=== hut build cost: {build_time}s of one brave's time ===")
        header = f"{'strategy':>10} {'lvl':>3}" + "".join(
            f"{('pop ' + str(m)):>10}" for m in (50, 100, 150, 190))
        print(header)
        for level in (1, 3):
            for name, strat in scenarios:
                s = Sim(strat, level, build_time=build_time).run()
                row = f"{name:>10} {level:>3}"
                for m in (50, 100, 150, 190):
                    t = s.milestones.get(m)
                    row += f"{t/60:>9.1f}m" if t else "      --  "
                print(row + f"   ({len(s.huts)} huts)")
