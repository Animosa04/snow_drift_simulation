import simpy
from enum import Enum
import random


class State(Enum):
    DIG = 0  # loses a lot of body heat
    NO_ACTION = 1  # loses a bit of body heat? why would someone choose this option, it's stupid
    TURN_ON_HEATER = 2  # gain body heat


class Human(object):
    def __init__(self, env, simulation, name):
        self.env = env
        simulation.agents.append(self)
        self.state = State.NO_ACTION
        self.body_temperature = 37
        self.name = name
        self.simulation = simulation

    def is_alive(self):
        return self.body_temperature > 35.0

    def step(self):
        # while self.is_alive():
        self.decide_what_to_do()
        if self.state == State.DIG:
            print(self.name + ": Digging")
            self.simulation.snow_drift.get(1)
            print("Snow drift size: " + str(self.simulation.snow_drift.level))
            # reduce body heat
            # reduce energy
        elif self.state == State.NO_ACTION:
            print(self.name + ": No action")
        else:
            print(self.name + ": Turning on heating")
        yield self.env.timeout(0)

    def decide_what_to_do(self):
        self.state = random.choice(list(State))


# TODO: this should be an interrupted shared process


class Car(object):
    def __init__(self, env):
        self.env = env
        self.battery_level = 100

    def get_battery_level(self):
        return self.battery_level
