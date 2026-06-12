

import simpy
import random
import time

###DENNA HER FUNKER LOOLLLLLL!!!###
#V2.0 - I denne versjonen så venter bravsa til de er 3 i hyttene før to av de går og lager ny hytte, men noe er feil!

env = simpy.Environment()

population = [6]
hytteantall = [0]
time_list = [0]
breething_duration = 97

class Tribe(object):

    def __init__(self, env):
        self.population = simpy.Container(env, init=6, capacity=200)
        self.hytteantall = simpy.Container(env, init=0, capacity=100)
        self.env = env

class Hut(object):

    def __init__(self, env, braves = None):
        self.action = env.process(self.breething_process())
        self.env = env
        self.braves = [] if braves is None else braves

    def breething_process(self): #denne føder en brave
        while True:
                yield self.env.timeout(breething_duration)
                tribe.population.put(1) #dette er han som ble født når hytta er ferdig
                population.append(tribe.population.level) #globale variablern
                time_list.append(env.now)
                print(f'Breething Completed! Population is now {tribe.population.level} at {env.now} seconds!')
                brave = Brave(env)
                yield self.env.process(self.add_brave(brave))
                yield self.env.process(self.check_hut_full())

    def add_brave(self, brave): #denne legger braven til i hytta og til braves lista
        self.braves.append(brave)
        brave.hut = self
        print(f'Brave added to hut. {len(self.braves)} in hut')
        yield env.timeout(1)

    def check_hut_full(self):
        if len(self.braves) == 3:
            yield self.env.process(self.split())

    def split(self):
        yield env.timeout(random.randint(15, 40))
        new_hut = Hut(env, self.braves[2:])
        print(f'Hut full! New hut created')
        self.braves[0].hut = new_hut
        self.braves[1].hut = new_hut
        new_hut.braves = self.braves[2:]
        self.braves = self.braves[:2]

        #så adde disse hyttene til antallet.
        tribe.hytteantall.put(1)  # vi adder 1 til triben sin hytteantall
        hytteantall.append(tribe.hytteantall.level)  # vi adder til den globale hytteantall variablen for plotting

class Brave(object):
    def __init__(self, env, hut=None):
        self.hut = None
        self.env = env
        self.action = env.process(self.create_hut(env))

    def create_hut(self, env):
        while self.hut is None:
            yield self.env.timeout(random.randint(15,40))
            self.hut = Hut(env)
            tribe.hytteantall.put(1) #vi adder 1 til triben sin hytteantall
            hytteantall.append(tribe.hytteantall.level)   # vi adder til den globale hytteantall variablen for plotting
            time_list.append(env.now)
            print(f'hut finished at {env.now} Current huts are {tribe.hytteantall.level}')

def stoppe_program():
    print("da stopper vi")



if __name__ == "__main__":
    tribe = Tribe(env)

    for x in range(6):
        Braveru = Brave(env)

    env.run(until=500)


"""



#V1.0 SOM FUNGERER. HER ER DET 1 BRAVE I HYTTA OG KOMMER DET EN TIL LAGES DET EN HYTTE MED EN GANG
import simpy
import random

###TESTVERSJON###

env = simpy.Environment()

LVL1_breething_duration = 97
population = [6]
hytteantall = [0]
time_list = [0]

class Tribe(object):

    def __init__(self, env):
        self.population = simpy.Container(env, init=6, capacity=200)
        self.hytteantall = simpy.Container(env, init=0, capacity=200)
        self.env = env


class Hut(object):
    number_of_huts = 0
    instances = []

    def __init__(self, env, braves = None):
        self.action = env.process(self.breething_process())
        self.env = env
        self.braves = []
        Hut.number_of_huts += 1
        self.instances.append(self)

    def breething_process(self):
        while True:
            yield self.env.timeout(LVL1_breething_duration)
            # We yield the process that process() returns
            # to wait for it to finish
            if tribe.population.level == 200:
                env.process(stoppe_program(env))
            else:
                # tribe.population.put(1)
                # population.append(tribe.population.level)
                # time_list.append(env.now)
                print(f'Breething completed! Population is now {Brave.number_of_braves} at {env.now} seconds')
                brave = Brave(env)

class Brave(object):
    number_of_braves = 0
    instances = []
    def __init__(self, env, hut=None):
        self.hut = None
        self.env = env
        self.action = env.process(self.create_hut(env))
        Brave.number_of_braves += 1
        self.instances.append(self)

    def create_hut(self, env):
        while self.hut is None:
            yield self.env.timeout(random.randint(5,50))
            self.hut = Hut(env)
            self.hut.braves.append(self)
            # tribe.hytteantall.put(1) #vi adder 1 til triben sin hytteantall
            # hytteantall.append(tribe.hytteantall.level)   # vi adder til den globale hytteantall variablen for plotting
            # time_list.append(env.now)
            print(f'hut finished at {env.now} Current huts are {Hut.number_of_huts}')

def stoppe_program():
    print("da stopper vi")

def print_empty_huts():
    empty_huts = [hut for hut in Hut.instances if hut.braves is None]
    print(f"Empty huts: {len(empty_huts)}")

def print_homeless_braves():
    homeless_braves = [brave for brave in Brave.instances if brave.hut is None]
    print(f"Homeless braves: {len(homeless_braves)}")



if __name__ == "__main__":
    tribe = Tribe(env)

    for x in range(6):
        brave = Brave(env)

    while True:
        # Run simulation for 10 seconds
        env.run(until=500)

        # Call function to print empty huts
        print_empty_huts()
        print_homeless_braves()
        print(f'number of huts: {Hut.number_of_huts}')
        print(f'number of braves:  {Brave.number_of_braves}')
"""



