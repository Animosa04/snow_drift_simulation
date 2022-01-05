import datetime
import pandas as pd
from parameters import *
FILE_PATH = "./simulation_results/"


class Monitor():
    def __init__(self, simulation, filename):
        self.simulation_id = filename + "_" + \
            datetime.datetime.now().strftime("%d%m%Y_%H%M%S")
        self.simulation = simulation
        self.data = pd.DataFrame(
            columns=['Agent', 'Step', 'Decision', 'Body temperature', 'Energy', 'Car battery level', 'Snow drift size'])
        self.simulation_metadata = pd.DataFrame(
            columns=['Simulation', 'Time', 'Snow drift', 'Steps', 'Number of agents', 'Digging coefficient',
                     'Starting body temperature', 'Body temperature decrease when DIGGING',
                     'Body temperature decrease when NO_ACTION', 'Body temperature increase when TURN_ON_HEATER',
                     'Starting energy', 'Energy decrease when DIGGING', 'Energy increase when NO_ACTION',
                     'Energy increase when TURN_ON_HEATER', 'Starting car battery_level', 'Car battery level decrease when TURN_ON_HEATER'])

    def append_to_result(self, agent, step, snow_drift):
        entry = {'Agent': agent.name,
                 'Step': step,
                 'Decision': agent.state.name,
                 'Body temperature': agent.body_temperature,
                 'Energy': agent.energy,
                 'Car battery level': agent.car.battery_level,
                 'Snow drift size': snow_drift.level}
        self.data = self.data.append(entry, ignore_index=True)

    def make_metadata(self):
        entry = {'Simulation': self.simulation_id,
                 'Time': self.simulation.time_elapsed,
                 'Snow drift': SNOW_DRIFT_SIZE,
                 'Steps': self.simulation.steps,
                 'Number of agents': len(self.simulation.agents),
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

        self.simulation_metadata.to_csv(METADATA_FILE_NAME, mode='a',
                                        index=False, header=False)
