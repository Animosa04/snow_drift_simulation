import simpy
from enum import Enum
import random


class State(Enum):
    DIG = 0
    NO_ACTION = 1
    TURN_ON_HEATER = 2


class Human(object):
    def __init__(self, env, simulation, name):
        self.env = env
        simulation.agents.append(self)
        self.state = State.NO_ACTION
        self.body_temperature = 37
        self.energy = 100
        self.name = name
        self.simulation = simulation

    def is_alive(self):
        return self.body_temperature > 35.0

    def update_agent(self):
        if self.state == State.DIG:
            i = 1
        elif self.state == State.NO_ACTION:
            i = 1
        else:
            i = 1
        yield self.env.timeout(0)

    def decide_what_to_do(self):
        self.state = random.choice(list(State))
        print(self.name + ": " + str(self.state))
        yield self.env.timeout(0)


# TODO: this should be an interrupted shared process


class Car(object):
    def __init__(self, env):
        self.env = env
        self.battery_level = 100

    def get_battery_level(self):
        return self.battery_level
