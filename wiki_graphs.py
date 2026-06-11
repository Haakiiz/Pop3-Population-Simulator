"""
Generates the explanatory graphs for the popre.net wiki page on Huts.

Outputs (PNG, white background, wiki-friendly):
  wiki_graph_1_occupants.png  -- breeding time vs occupants per hut level,
                                 with the measured in-game data points overlaid
  wiki_graph_2_pop_bands.png  -- the population-band slowdown staircase
  wiki_graph_3_same_braves.png-- same 6 braves, different housing -> birth rate
  wiki_graph_4_strategies.png -- growth curves for cram/balanced/spread
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from strategy_sim import Sim, cram, balanced, spread, breed_time, BASE, TICKRATE

LEVEL_COLOR = {1: '#c0392b', 2: '#e67e22', 3: '#27ae60'}


def time_at_low_pop(level, braves):
    mult = 0.5 + 0.5 * braves
    return (BASE[level] * 30 / 100) / (mult * TICKRATE)


# ---------------------------------------------------------------- graph 1
def graph_occupants():
    fig, ax = plt.subplots(figsize=(8, 5.5))
    occupants = range(0, 6)
    cap = {1: 3, 2: 4, 3: 5}
    for lvl in (1, 2, 3):
        xs = [b for b in occupants if b <= cap[lvl]]
        ys = [time_at_low_pop(lvl, b) for b in xs]
        ax.plot(xs, ys, 'o-', color=LEVEL_COLOR[lvl], lw=2,
                label=f'Level {lvl} hut (formula)')

    # measured in-game points, both sessions, population < 10
    measured = {
        1: [(0, 197), (1, 97), (1, 100), (2, 64), (2, 55), (2, 71), (3, 48)],
        2: [(1, 65), (2, 47), (3, 34), (4, 27)],
        3: [(1, 48), (2, 30), (3, 22), (4, 18), (5, 14)],
    }
    for lvl, pts in measured.items():
        ax.scatter([p[0] for p in pts], [p[1] for p in pts], marker='x', s=70,
                   color=LEVEL_COLOR[lvl], zorder=5,
                   label=f'Level {lvl} measured in-game' if lvl == 1 else None)
    ax.scatter([], [], marker='x', s=70, color='black',
               label='Measured in-game (x)')

    ax.annotate('empty huts still breed\n(multiplier 0.5)',
                xy=(0, 192), xytext=(0.8, 165),
                arrowprops=dict(arrowstyle='->'), fontsize=9)
    ax.set_xlabel('Followers housed in the hut')
    ax.set_ylabel('Seconds per new brave')
    ax.set_title('Breeding time vs occupants (population < 10)\n'
                 r'$T = \frac{BaseSprogTime \times Band\%/100}{(0.5 + 0.5 \times occupants) \times 12.5}$')
    ax.set_xticks(list(occupants))
    ax.grid(alpha=0.3)
    handles, labels = ax.get_legend_handles_labels()
    keep = [i for i, l in enumerate(labels) if 'in-game' not in l or l.startswith('Meas')]
    ax.legend([handles[i] for i in keep], [labels[i] for i in keep])
    fig.tight_layout()
    fig.savefig('wiki_graph_1_occupants.png', dpi=130)


# ---------------------------------------------------------------- graph 2
def graph_pop_bands():
    fig, ax = plt.subplots(figsize=(8, 5.5))
    pops = range(0, 201)
    for lvl, braves, style in ((1, 1, '-'), (3, 1, '-'), (3, 5, '--')):
        ys = [breed_time(lvl, braves, p) for p in pops]
        ax.plot(pops, ys, style, color=LEVEL_COLOR[lvl], lw=2,
                label=f'Level {lvl} hut, {braves} occupant{"s" if braves > 1 else ""}')

    # measured band points (lvl 3, 5 occupants and 1 occupant)
    ax.scatter([6, 15, 25], [14, 19, 22], marker='x', s=70,
               color=LEVEL_COLOR[3], zorder=5)
    ax.scatter([6, 25], [48, 65], marker='x', s=70, color=LEVEL_COLOR[3],
               zorder=5, label='Measured in-game (x)')

    ax.annotate('breeding slows in steps every 10 population\n(bands are % of the 200 max)',
                xy=(100, breed_time(1, 1, 100)), xytext=(105, 170),
                arrowprops=dict(arrowstyle='->'), fontsize=9)
    ax.set_xlabel('Tribe population')
    ax.set_ylabel('Seconds per new brave')
    ax.set_title('Bigger tribe = slower huts: the population-band staircase')
    ax.grid(alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig('wiki_graph_2_pop_bands.png', dpi=130)


# ---------------------------------------------------------------- graph 3
def graph_same_braves():
    fig, ax = plt.subplots(figsize=(8, 5))
    # 6 braves, level 1 huts, population < 10 (band 30)
    arrangements = [
        ('2 full huts\n(3+3)', [3, 3]),
        ('3 huts\n(2+2+2)', [2, 2, 2]),
        ('6 huts\n(1 each)', [1] * 6),
        ('6 huts + 2 empty\n(1 each + 0+0)', [1] * 6 + [0, 0]),
    ]
    rates, labels = [], []
    for label, huts in arrangements:
        per_min = sum(60 / breed_time(1, b, 6) for b in huts)
        rates.append(per_min)
        labels.append(label)
    bars = ax.bar(labels, rates,
                  color=['#c0392b', '#e67e22', '#27ae60', '#16a085'])
    for bar, r in zip(bars, rates):
        ax.text(bar.get_x() + bar.get_width() / 2, r + 0.05, f'{r:.2f}',
                ha='center', fontweight='bold')
    ax.set_ylabel('New braves per minute (whole tribe)')
    ax.set_title('Same 6 braves, different housing — level 1 huts, population < 10\n'
                 'every occupied hut adds 1.0×, every extra occupant only 0.5×')
    ax.grid(alpha=0.3, axis='y')
    fig.tight_layout()
    fig.savefig('wiki_graph_3_same_braves.png', dpi=130)


# ---------------------------------------------------------------- graph 4
def graph_strategies():
    fig, axes = plt.subplots(1, 2, figsize=(11, 5), sharey=True)
    strategies = [('cram huts full', cram, '#c0392b'),
                  ('~2 per hut', balanced, '#e67e22'),
                  ('1 per hut', spread, '#27ae60')]
    for ax, lvl in zip(axes, (1, 3)):
        for name, strat, color in strategies:
            s = Sim(strat, lvl, build_time=60).run()
            xs = [t / 60 for t, _ in s.history]
            ys = [p for _, p in s.history]
            ax.plot(xs, ys, color=color, lw=2, label=name)
        ax.set_title(f'Level {lvl} huts')
        ax.set_xlabel('Minutes')
        ax.grid(alpha=0.3)
    axes[0].set_ylabel('Tribe population')
    axes[0].legend(title='Housing strategy')
    fig.suptitle('Growing from 6 braves to 190 — never wait for huts to fill\n'
                 '(~2 per hut wins when each hut costs 60 s of one brave\'s build time)')
    fig.tight_layout()
    fig.savefig('wiki_graph_4_strategies.png', dpi=130)


if __name__ == '__main__':
    graph_occupants()
    graph_pop_bands()
    graph_same_braves()
    graph_strategies()
    print('wrote wiki_graph_1..4 PNGs')
