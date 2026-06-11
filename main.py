import simpy
import random
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# To do liste:
#     Hyttene oppgrader seg. DONE!
#     forskjellig birth rate avhengig av populasjon! DONE!
#     automatisk laging av graf. DONE!
# Det må alltid være 2 som lager en hut, også på starten



###FUNGERNDE VERSJON
#V2.0 - I denne versjonen så venter bravsa til de er 3 i hyttene før to av de går og lager ny hytte

env = simpy.Environment()

base_sprog_time = {1: 4000, 2: 3000, 3: 2000}
# Raw P3CONST_SPROG%_POP_BAND values from constant.dat. The band is the
# tribe's population as a percentage of the 200 max (pop 0-9 -> 00_04, etc.)
population_band_factors = {
    "00_04": 30,  # population 0-9
    "05_09": 35,  # population 10-19
    "10_14": 40,  # population 20-29
    "15_19": 50,  # ...etc
    "20_24": 60,
    "25_29": 70,
    "30_34": 80,
    "35_39": 90,
    "40_44": 100,
    "45_49": 110,
    "50_54": 120,
    "55_59": 130,
    "60_64": 140,
    "65_69": 150,
    "70_74": 160,
    "75_79": 170,
    "80_84": 180,
    "85_89": 190,
    "90_94": 195,
    "95_99": 200,
}

graph_population = [6]
graph_time = [0]
graph_huts = [0]

MAX_POPULATION = 200

def get_population_band_factor(Brave, population_band_factors):
    population = Brave.number_of_braves
    band_index = min(int(population / MAX_POPULATION * 100) // 5, 19)
    return list(population_band_factors.values())[band_index]

#gets multiplier from this code in the constant.dat "# X 0 - 0.5, 1 - 1.0, 2 - 1.5, 3 - 2.0 ...."
#even an empty hut breeds, at half the rate of a 1-brave hut (confirmed by
#measured times: lvl1/0 braves = 197s, lvl3/0 braves/pop14 = 120s)
hut_multiplier = {
        0:0.5,
        1:1,
        2:1.5,
        3:2,
        4:2.5,
        5:3,
    }

# The game advances its breeding logic at 12.5 game turns per second.
# A hut needs base_sprog_time * band% / 100 "sprog points" for a birth and
# earns hut_multiplier points per game turn, so the breeding time is:
#   T_seconds = (base_sprog_time * band% / 100) / (hut_multiplier * 12.5)
# Validated against measured in-game times in formula_validation.py
# (mean error < 5%, no fitted constants).
TICKRATE = 12.5

def find_breething_duration(base_sprog_time, braves_antall):
    population_band = get_population_band_factor(Brave, population_band_factors)
    mult = hut_multiplier[min(braves_antall, 5)]
    breething_duration = (base_sprog_time * population_band / 100) / (mult * TICKRATE)
    return max(1.0, breething_duration)

class Tribe(object):

    def __init__(self, env):
        self.population = simpy.Container(env, init=6, capacity=200)
        self.hytteantall = simpy.Container(env, init=0, capacity=200)
        self.env = env
        self.startgraphcounter = env.process(self.graph_maker(env, Brave))

    def graph_maker(self, env, Brave):
        while True:
            yield env.timeout(10)
            graph_time.append(env.now)
            graph_population.append(Brave.number_of_braves)

class Hut(object):
    number_of_huts = 0
    instances = []

    def __init__(self, env, braves=None, level=1, capacity=3, sprog_rate=97):
        self.action = env.process(self.breething_process())
        self.action = env.process(self.hut_upgrade())
        self.env = env
        self.braves = [] if braves is None else braves
        Hut.number_of_huts += 1
        self.instances.append(self)
        self.level = level
        self.capacity = capacity
        self.sprog_rate = sprog_rate

    @classmethod
    def iterate_instances(cls):
        for instance in cls.instances:
            yield instance

    def breething_process(self): #denne føder en brave
        while True:
            capped_level = min(self.level, max(base_sprog_time.keys()))
            self.sprog_rate = find_breething_duration(base_sprog_time[capped_level], len(self.braves))
            #print(f'Sprog rate er {self.sprog_rate}: \n hutlvl: {self.level} \n beboere: {len(self.braves)} \n totalPOP: {graph_population[-1]}  ')
            yield self.env.timeout(self.sprog_rate)
            brave = Brave(env)
            print(f'Brave ID: {brave.braveID} Born! Population is now {Brave.number_of_braves} at {env.now} seconds!')
            yield self.env.process(self.add_brave(brave))
            yield self.env.process(self.check_hut_full())

    def hut_upgrade(self):
        while True:
            yield self.env.timeout(200)
            self.level += 1
            self.capacity += 1
            brave = Brave(env)
            yield self.env.process(self.add_brave(brave))
            print(f'Hut upgrade! level is now {self.level}')


    def add_brave(self, brave): #denne legger braven til i hytta og til braves lista
        self.braves.append(brave)
        brave.hut = self
        print(f'Brave ID: {brave.braveID} added to hut. {len(self.braves)} in hut')
        yield env.timeout(1)

    def check_hut_full(self):
        if len(self.braves) == self.capacity:
            print('Braves in the Hut')
            for brave in self.braves:
                print(f'BraveID: {brave.braveID}')
            yield self.env.process(self.split())

    def split(self):
        yield env.timeout(random.randint(1,15))
        moving = list(self.braves[2:])
        new_hut = Hut(env, moving)
        for b in moving:
            b.hut = new_hut
        self.braves = self.braves[:2]
        # print(f'Hut full! New hut created.')

class Brave(object):
    number_of_braves = 0
    instances = []

    def __init__(self, env, hut=None, braveID = None):
        self.hut = None
        self.env = env
        self.action = env.process(self.create_hut(env))
        Brave.number_of_braves += 1
        self.instances.append(self)
        self.braveID = len(Brave.instances)

    def create_hut(self, env):
        while self.hut is None:
            yield self.env.timeout(random.randint(15,40))
            self.hut = Hut(env)
            self.hut.braves.append(self)
            self.hut.braves
            print(f'Homeless braveID: {self.braveID} created hut and moved in. {len(self.hut.braves)} rooms taken')
            print(f'hut finished at {env.now} Current huts are {Hut.number_of_huts}')

def stoppe_program():
    print("da stopper vi")


def print_empty_huts():
    empty_huts = [hut for hut in Hut.instances if hut.braves == []]
    print(f"Empty huts: {len(empty_huts)}")

def print_homeless_braves():
    homeless_braves = [brave for brave in Brave.instances if brave.hut is None]
    print(f"Homeless braves: {len(homeless_braves)}")


if __name__ == "__main__":
    tribe = Tribe(env)
    for x in range(6):
        Braveru = Brave(env)

    for checkpoint in [300, 500, 800, 1200]:
        env.run(until=checkpoint)
        print(f'\n--- t={checkpoint} ---')
        print(f'Population: {Brave.number_of_braves}')
        print(f'Huts:       {Hut.number_of_huts}')
        print_homeless_braves()

    print(f'\nFinal population data (every 10 ticks):')
    print(graph_population)

    plt.plot(graph_time, graph_population)
    plt.xlabel('Time (ticks)')
    plt.ylabel('Population')
    plt.title('Populous 3 — Tribe Population over Time')
    plt.savefig('population_graph.png')
    print('\nGraph saved to population_graph.png')



"""
#V1.0 SOM FUNGERER. HER ER DET 1 BRAVE I HYTTA OG KOMMER DET EN TIL LAGES DET EN HYTTE MED EN GANG
import simpy
import random

###DENNA HER FUNKER LOOLLLLLL!!!###

env = simpy.Environment()

breething_duration = 97
population = [6]
hytteantall = [0]
time_list = [0]

class Tribe(object):

    def __init__(self, env):
        self.population = simpy.Container(env, init=6, capacity=200)
        self.hytteantall = simpy.Container(env, init=0, capacity=100)
        self.env = env


class Hut(object):
    def __init__(self, env):
        self.action = env.process(self.breething_process())
        self.env = env

    def breething_process(self):
        while True:
            yield self.env.timeout(breething_duration)
            # We yield the process that process() returns
            # to wait for it to finish
            if tribe.population.level == 200:
                env.process(stoppe_program(env))
            else:
                tribe.population.put(1)
                population.append(tribe.population.level)
                time_list.append(env.now)
                print(f'Breething completed! Population is now {tribe.population.level} at {env.now} seconds')
                brave = Brave(env)

class Brave(object):
    def __init__(self, env, hut=None):
        self.hut = None
        self.env = env
        self.action = env.process(self.create_hut(env))

    def create_hut(self, env):
        while self.hut is None:
            yield self.env.timeout(random.randint(5,50))
            self.hut = Hut(env)
            tribe.hytteantall.put(1) #vi adder 1 til triben sin hytteantall
            hytteantall.append(tribe.hytteantall.level)   # vi adder til den globale hytteantall variablen for plotting
            time_list.append(env.now)
            print(f'hut finished at {env.now} Current huts are {tribe.hytteantall.level}')

def stoppe_program():
    print("da stopper vi")



if __name__ == "__main__":
    tribe = Tribe(env)

    brave = Brave(env)


    env.run(until=1000)

"""


