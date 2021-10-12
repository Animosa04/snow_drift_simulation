import simpy
import random

# TODO: add monitoring


class Simulation(object):
    def __init__(self, env):
        snow_drift_size = random.randint(50, 100)
        self.snow_drift = simpy.Container(env, init=5)
        self.agents = []

    def get_number_of_agents(self):
        return len(self.agents)

    def goal_reached(self):
        return self.snow_drift.level <= 0

    def all_agents_dead(self):
        for agent in self.agents:
            if agent.is_alive():
                return False
        return True

    def run(self, env):
        while not self.goal_reached():
            for agent in self.agents:
                yield env.process(agent.step())
            print(env.now)
            yield env.timeout(1)
