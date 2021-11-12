import simpy
from parameters import *
from agents import State
import pandas as pd
import numpy as np
import datetime

FILE_PATH = "./simulation_results/"
FILE_NAME = "random"


class Simulation(object):
    def __init__(self, env):
        self.snow_drift = simpy.Container(
            env, init=SNOW_DRIFT_SIZE)
        self.agents = []
        self.data = pd.DataFrame(
            columns=['Agent', 'Step', 'Decision', 'Body temperature', 'Energy', 'Car battery level', 'Snow drift size'])

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
        while not self.goal_reached() or self.all_agents_dead():
            yield env.process(self.step(env))
        self.save_simulation_data()
        print(self.data)

    def step(self, env):
        step = env.now
        for agent in self.agents:
            yield env.process(agent.decide_what_to_do())

        for agent in self.agents:
            yield env.process(agent.update_agent())
            if(agent.state == State.DIGGING):
                # snow_shoveled = round(agent.energy*DIGGING_COEFFICIENT, 2)
                # TODO: no floats, but figure out a better way to do this based on energy
                self.snow_drift.get(1)
                print(self.snow_drift.level)
            self.append_to_result(agent, step, self.snow_drift)
        yield env.timeout(1)

    def append_to_result(self, agent, step, snow_drift):
        entry = {'Agent': agent.name,
                 'Step': step,
                 'Decision': agent.state.name,
                 'Body temperature': agent.body_temperature,
                 'Energy': agent.energy,
                 'Car battery level': agent.car.battery_level,
                 'Snow drift size': snow_drift.level}
        self.data = self.data.append(entry, ignore_index=True)

    def save_simulation_data(self):
        file_name = FILE_PATH + FILE_NAME + "_" + \
            datetime.datetime.now().strftime("%d%m%Y_%H%M%S") + ".csv"
        self.data.to_csv(file_name, index=False, header=True)
