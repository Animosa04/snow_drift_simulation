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
    def __init__(self, env, simulation, name, seed):
        self.env = env
        self.simulation = simulation
        simulation.agents.append(self)
        self.name = name
        self.state = State.NO_ACTION
        self.body_temperature = MAX_BODY_TEMPERATURE
        self.energy = MAX_ENERGY
        self.car = Car(self.env)
        self.past_actions = []
        random.seed(seed)

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
        # Make decision about what to do
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


class EpsilonGreedyQLearningMultiarmedBandit(Agent):
    q_table = {}
    rewards_for_step = {}

    def decide_what_to_do(self):
        self.calculate_rewards_for_step()

        # draw a 0 or 1 from a binomial distribution, with epsilon % likelihood of drawing a 1
        explore = random.binomial(1, EPSILON)
        if explore == 1 or len(self.past_actions) == 0:
            # choose randomly between all arms
            self.state = random.choice(list(State))
        else:
            # choose optimal arm
            self.state = max(self.selected_actions,
                             key=self.selected_actions.get)

        # Save decision in action history
        self.past_actions[self.state] += 1

        # Update Q-table
        self.q_table[self.state] += 1/(self.past_actions[self.state]) * \
            (self.rewards_for_step[self.state] - self.q_table[self.state])

        yield self.env.timeout(0)

    # def calculate_rewards_for_step(self):
