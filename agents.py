import simpy
from enum import Enum
import random
from car import Car
from parameters import *


class State(Enum):
    DIGGING = 0
    NO_ACTION = 1
    TURN_ON_HEATER = 2


class Agent(object):
    def __init__(self, env, simulation, name):
        self.env = env
        self.simulation = simulation
        simulation.agents.append(self)
        self.name = name
        self.state = State.NO_ACTION
        self.body_temperature = MAX_BODY_TEMPERATURE
        self.energy = MAX_ENERGY
        self.car = Car(self.env)
        self.past_actions = []
        random.seed(69)

    def is_alive(self):
        return self.body_temperature > 35.0

    def update_agent(self):
        if self.state == State.DIGGING:
            self.decrease_body_temperature(
                BODY_TEMPERATURE_DECREASE_WHEN_DIGGING)
            self.decrease_energy(ENERGY_DECREASE_WHEN_DIGGING)
        elif self.state == State.NO_ACTION:
            self.decrease_body_temperature(
                BODY_TEMPERATURE_DECREASE_WHEN_NO_ACTION)
            self.increase_energy(ENERGY_INCREASE_WHEN_NO_ACTION)
        else:
            self.increase_body_temperature(
                BODY_TEMPERATURE_INCREASE_WHEN_TURN_ON_HEATER)
            self.increase_energy(ENERGY_INCREASE_WHEN_TURN_ON_HEATER)
            self.car.decrease_battery_level()
        yield self.env.timeout(0)

    def decide_what_to_do(self):
        # Make decision about what to
        self.state = random.choice(list(State))

        # Save decision in action history
        self.past_actions.append(self.state)

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
        if self.energy < 0:
            self.energy = 0


# TODO: implement Q-learning
class SlightlySmarterAgent(Agent):
    def decide_what_to_do(self):

        # Save decision in action history
        self.past_actions.append(self.state)

        yield self.env.timeout(0)
