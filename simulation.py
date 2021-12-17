import simpy
from parameters import *
from agents import State
import pandas as pd
import numpy as np
import datetime
import time

FILE_PATH = "./simulation_results/"
FILE_NAME = "random"


class Simulation(object):
    def __init__(self, env):
        self.snow_drift = simpy.Container(
            env, init=SNOW_DRIFT_SIZE)
        self.agents = []
        self.data = pd.DataFrame(
            columns=['Agent', 'Step', 'Decision', 'Body temperature', 'Energy', 'Car battery level', 'Snow drift size'])
        self.simulation_metadata = pd.DataFrame(
            columns=['Simulation', 'Time', 'Snow drift', 'Steps', 'Number of agents', 'Digging coefficient',
                     'Starting body temperature', 'Body temperature decrease when DIGGING',
                     'Body temperature decrease when NO_ACTION', 'Body temperature increase when TURN_ON_HEATER',
                     'Starting energy', 'Energy decrease when DIGGING', 'Energy increase when NO_ACTION',
                     'Energy increase when TURN_ON_HEATER', 'Starting car battery_level', 'Car battery level decrease when TURN_ON_HEATER'])
        self.simulation_id = FILE_NAME + "_" + \
            datetime.datetime.now().strftime("%d%m%Y_%H%M%S")
        self.time_elapsed = 0.0
        self.steps = 0

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
        start = time.time()
        while not self.goal_reached() or self.all_agents_dead():
            yield env.process(self.step(env))
        end = time.time()
        self.time_elapsed = end - start
        self.make_metadata(self.simulation_id)
        self.save_simulation_data()
        print(self.data)

    def step(self, env):
        step = env.now
        for agent in self.agents:
            if agent.is_alive() and not self.goal_reached():
                yield env.process(agent.decide_what_to_do())
            if agent.is_alive() and self.goal_reached():
                agent.state = State.NO_ACTION

        for agent in self.agents:
            if agent.is_alive() and not self.goal_reached():
                yield env.process(agent.update_agent())
                if(agent.state == State.DIGGING):
                    snow_shoveled = round(agent.energy*DIGGING_COEFFICIENT, 2)
                    if(snow_shoveled >= self.snow_drift.level):
                        self.snow_drift.get(self.snow_drift.level)
                    else:
                        self.snow_drift.get(snow_shoveled)
                    print(self.snow_drift.level)
            self.append_to_result(agent, step, self.snow_drift)
        self.steps += 1
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

    def make_metadata(self, simulation_id):
        entry = {'Simulation': simulation_id,
                 'Time': self.time_elapsed,
                 'Snow drift': SNOW_DRIFT_SIZE,
                 'Steps': self.steps,
                 'Number of agents': len(self.agents),
                 'Digging coefficient': DIGGING_COEFFICIENT,
                 'Starting body temperature': MAX_BODY_TEMPERATURE,
                 'Body temperature decrease when DIGGING': BODY_TEMPERATURE_DECREASE_WHEN_DIGGING,
                 'Body temperature decrease when NO_ACTION': BODY_TEMPERATURE_DECREASE_WHEN_NO_ACTION,
                 'Body temperature increase when TURN_ON_HEATER': BODY_TEMPERATURE_DECREASE_WHEN_NO_ACTION,
                 'Starting energy': MAX_ENERGY,
                 'Energy decrease when DIGGING': ENERGY_DECREASE_WHEN_DIGGING,
                 'Energy increase when NO_ACTION': ENERGY_INCREASE_WHEN_NO_ACTION,
                 'Energy increase when TURN_ON_HEATER': ENERGY_INCREASE_WHEN_TURN_ON_HEATER,
                 'Starting car battery_level': MAX_CAR_BATTERY_LEVEL,
                 'Car battery level decrease when TURN_ON_HEATER': CAR_BATTERY_DECREASE_WHEN_TURN_ON_HEATER
                 }
        self.simulation_metadata = self.simulation_metadata.append(
            entry, ignore_index=True)

    def save_simulation_data(self):

        results_file_name = FILE_PATH + self.simulation_id + ".csv"
        self.data.to_csv(results_file_name,
                         index=False, header=True)

        metadata_file_name = FILE_PATH + self.simulation_id + "_metadata.csv"
        self.simulation_metadata.to_csv(
            metadata_file_name, index=False, header=True)
