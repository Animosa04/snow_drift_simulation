import simpy
from enum import Enum
import random

MAX_BODY_TEMPERATURE = 37
MAX_ENERGY = 100
MAX_BATTERY_LEVEL = 100


class State(Enum):
    DIGGING = 0
    NO_ACTION = 1
    TURN_ON_HEATER = 2


class Human(object):
    def __init__(self, env, simulation, name):
        self.env = env
        self.simulation = simulation
        simulation.agents.append(self)
        self.name = name
        self.state = State.NO_ACTION
        self.body_temperature = 37  # maybe a container to have an upper limit?
        self.energy = MAX_ENERGY
        self.car = Car(self.env)

    def is_alive(self):
        return self.body_temperature > 35.0

    def update_agent(self):
        if self.state == State.DIGGING:
            self.decrease_body_temperature(0.02)
            self.decrease_energy(1)
        elif self.state == State.NO_ACTION:
            # TODO: do what exactly, hmmm...
            i = 1
        else:
            self.increase_body_temperature(0.02)
            self.increase_energy(1)
            self.decrease_car_battery_level(1)
        yield self.env.timeout(0)

    def decide_what_to_do(self):
        self.state = random.choice(list(State))
        print(self.name + ": " + str(self.state))
        yield self.env.timeout(0)

    def increase_body_temperature(self, amount):
        self.body_temperature += amount
        if self.body_temperature > MAX_BODY_TEMPERATURE:
            self.body_temperature = MAX_BODY_TEMPERATURE

    def decrease_body_temperature(self, amount):
        self.body_temperature -= amount

    def increase_energy(self, amount):
        self.energy += amount
        if self.energy > MAX_ENERGY:
            self.energy = MAX_ENERGY

    def decrease_energy(self, amount):
        self.energy -= amount

    def decrease_car_battery_level(self, amount):
        self.car.battery_level -= amount
        if self.car.battery_level < 0:  # do we really need this check?
            self.car.battery_level = 0


class Car(object):
    def __init__(self, env):
        self.env = env
        self.battery_level = MAX_BATTERY_LEVEL
