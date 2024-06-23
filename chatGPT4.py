import simpy
import random
import matplotlib.pyplot as plt

class Tribe:
    def __init__(self, env):
        self.env = env
        self.braves = [Brave(env, self, i) for i in range(6)]
        self.huts = []
        self.population = len(self.braves)

    def build_hut(self, brave):
        build_time = random.uniform(20, 50)
        yield self.env.timeout(build_time)
        hut = Hut()
        hut.add_brave(brave)
        self.huts.append(hut)


class Hut:
    def __init__(self):
        self.braves = []
        self.capacity = 3

    def add_brave(self, brave):
        if len(self.braves) < self.capacity:
            self.braves.append(brave)
            brave.hut = self
        else:
            print(f"Cannot add Brave {brave.id} to hut because the hut is full")



class Brave:
    def __init__(self, env, tribe, id):
        self.env = env
        self.tribe = tribe
        self.id = id
        self.hut = None
        self.action = env.process(self.run())

    def run(self):
        while True:
            if not self.hut and self.tribe.population < 200:
                print(f"Brave {self.id} starts building a hut at {self.env.now}")
                yield self.env.process(self.tribe.build_hut(self))

            elif self.hut and len(self.hut.braves) < 3 and self.tribe.population < 200:
                yield self.env.timeout(97)
                new_brave = Brave(self.env, self.tribe, self.tribe.population)

                # Find the least occupied hut
                least_occupied_hut = min(self.tribe.huts, key=lambda hut: len(hut.braves))
                least_occupied_hut.add_brave(new_brave)

                self.tribe.braves.append(new_brave)
                self.tribe.population += 1
                print(f"Brave {new_brave.id} is born at {self.env.now} in hut with Brave {self.id}")

            else:
                return


def collect_population_data(env, tribe, interval):
    population_data = []
    while True:
        yield env.timeout(interval)
        population_data.append(tribe.population)
        if tribe.population >= 200:
            return population_data

env = simpy.Environment()
tribe = Tribe(env)
population_data_process = env.process(collect_population_data(env, tribe, 10))
env.run()

population_data = population_data_process.value
time_data = [i * 10 for i in range(len(population_data))]

plt.plot(time_data, population_data)
plt.xlabel('Time (seconds)')
plt.ylabel('Population')
plt.title('Population Growth Over Time')
plt.show()



