import simpy
import random
from agents import State
import pandas as pd
import numpy as np

# TODO: decide what stuff to save


class Simulation(object):
    def __init__(self, env):
        snow_drift_size = random.randint(50, 100)
        self.snow_drift = simpy.Container(
            env, init=25.0)  # TODO: use random size
        self.agents = []
        self.data = pd.DataFrame(
            columns=['Agent', 'Step', 'Decision', 'Body temperature'])

    def get_number_of_agents(self):
        return len(self.agents)

    def goal_reached(self):
        return self.snow_drift.level <= 0

    def all_agents_dead(self):
        for agent in self.agents:
            if agent.is_alive():
                return False
        return True
    # TODO: if an agent is dead, remove from list of agents?

    def run(self, env):
        while not self.goal_reached():  # TODO: stop when all agents are dead? or when only 1 left because there is no game anymore?
            yield env.process(self.step(env))
        self.data.to_csv(
            r'./simulation_result.csv', index=False, header=True)
        print(self.data)

    def step(self, env):
        step = env.now

        for agent in self.agents:
            yield env.process(agent.decide_what_to_do())

        for agent in self.agents:
            yield env.process(agent.update_agent())
            if(agent.state == State.DIG):
                self.snow_drift.get(1)

            entry = {'Agent': agent.name,
                     'Step': step,
                     'Decision': agent.state,
                     'Body temperature': agent.body_temperature}
            self.data = self.data.append(entry, ignore_index=True)

        print("Step: " + str(env.now))
        print("Snow drift size: " + str(self.snow_drift.level))

        yield env.timeout(1)
