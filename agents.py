import simpy
from enum import Enum
from numpy import random
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
        self.past_actions = {}
        random.seed(seed)

    def is_alive(self):
        if self.body_temperature < 35.0:
            print(self.name + " is not alive")
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
        print(self.name + " selected action " + str(self.state))

        # Save decision in action history
        # self.past_actions.append(self.state)

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


class EpsilonGreedyAgent(Agent):
    def __init__(self, env, simulation, name, seed):
        super().__init__(env, simulation, name, seed)
        self.actions_rewards = {}

    def decide_what_to_do(self):
        # Draw a 0 or 1 from a binomial distribution, with epsilon % likelihood of drawing a 1
        explore = random.binomial(1, EPSILON)

        if explore == 1 or len(self.actions_rewards) == 0:
            # Choose randomly between all arms
            self.state = random.choice(list(State))
            print(self.name + " selected action " +
                  str(self.state) + " randomly")
        else:
            # Choose best arm
            self.state = max(self.actions_rewards,
                             key=self.actions_rewards.get)
            print(self.name + " selected action " + str(self.state))

        yield self.env.timeout(0)

    def reward_for_step(self, snow_drift_decrease):
        # Base reward - assign if snow drift has decreased
        # Collaboration reward is included in the base reward
        self.actions_rewards[self.state] = self.actions_rewards.get(self.state, 0) + \
            snow_drift_decrease

        # Reward for exploiting an agent successfully
        if snow_drift_decrease > 0 and self.state != State.DIGGING:
            for agent in self.simulation.agents:
                if agent.state == State.DIGGING:
                    self.actions_rewards[self.state] = self.actions_rewards.get(self.state, 0) + \
                        EXPLOITATION_REWARD
                    print(agent.name + ' was exploited by ' + self.name)

        # Reward for saving energy when energy is low
        if (self.state == State.NO_ACTION or self.state == State.TURN_ON_HEATER) and self.energy < ENERGY_SAVING_THRESHOLD:
            self.actions_rewards[self.state] = self.actions_rewards.get(
                self.state, 0) + ENERGY_SAVING_REWARD
            print(self.name + " rewarded for saving energy when energy is low")

        # Reward for saving body heat when body temperature is low
        if self.state == State.TURN_ON_HEATER and self.car.battery_level > 0 and self.body_temperature < BODY_TEMPERATURE_SAVING_THRESHOLD:
            self.actions_rewards[self.state] = self.actions_rewards.get(
                self.state, 0) + BODY_TEMPERATURE_SAVING_REWARD
            print(
                self.name + " rewarded for saving body heat when body temperature is low")
        elif self.state == State.NO_ACTION and self.body_temperature < BODY_TEMPERATURE_SAVING_THRESHOLD:
            self.actions_rewards[self.state] = self.actions_rewards.get(
                self.state, 0) + BODY_TEMPERATURE_SAVING_REWARD
            print(
                self.name + " rewarded for saving body heat when body temperature is low")

        print(self.name + " rewards for actions: ")
        for key, value in self.actions_rewards.items():
            print(key, value)

        yield self.env.timeout(0)


class QLearningAgent(Agent):
    def __init__(self, env, simulation, name, seed):
        super().__init__(env, simulation, name, seed)
        self.q_table = {}
        self.expected_reward_for_next_step = {}

    def decide_what_to_do(self):
        # Draw a 0 or 1 from a binomial distribution, with epsilon % likelihood of drawing a 1
        explore = random.binomial(1, EPSILON)

        if explore == 1 or len(self.q_table) == 0:
            # Choose randomly between all arms
            self.state = random.choice(list(State))
            print(self.name + " selected action " +
                  str(self.state) + " randomly")
        else:
            # Choose best arm
            self.state = max(self.q_table,
                             key=self.q_table.get)
            print(self.name + " selected action " + str(self.state))

        yield self.env.timeout(0)

    def update_q_table(self, snow_drift_decrease):
        print(self.name + " old Q-table: ")
        for key, value in self.q_table.items():
            print(key, value)

        reward = self.calculate_reward(snow_drift_decrease)
        max_expected_reward_for_next_step = self.get_biggest_expected_reward()

        self.q_table[self.state] = self.q_table.get(self.state, 0) + LEARNING_RATE * (
            reward + max_expected_reward_for_next_step - self.q_table.get(self.state, 0))

        print(self.name + " new Q-table: ")
        for key, value in self.q_table.items():
            print(key, value)

        yield self.env.timeout(0)

    def calculate_reward(self, snow_drift_decrease):
        # Base reward - assign if snow drift has decreased
        # Collaboration reward is included in the base reward
        reward = snow_drift_decrease

        # Reward for exploiting an agent successfully
        if snow_drift_decrease > 0 and self.state != State.DIGGING:
            for agent in self.simulation.agents:
                if agent.state == State.DIGGING:
                    reward = reward + EXPLOITATION_REWARD
                    print(agent.name + ' was exploited by ' + self.name)

        # Reward for saving energy when energy is low
        if (self.state == State.NO_ACTION or self.state == State.TURN_ON_HEATER) and self.energy < ENERGY_SAVING_THRESHOLD:
            reward = reward + ENERGY_SAVING_REWARD
            print(self.name + " rewarded for saving energy when energy is low")

        # Reward for saving body heat when body temperature is low
        if self.state == State.TURN_ON_HEATER and self.car.battery_level > 0 and self.body_temperature < BODY_TEMPERATURE_SAVING_THRESHOLD:
            reward = reward + BODY_TEMPERATURE_SAVING_REWARD
            print(
                self.name + " rewarded for saving body heat when body temperature is low")
        elif self.state == State.NO_ACTION and self.body_temperature < BODY_TEMPERATURE_SAVING_THRESHOLD:
            reward = reward + BODY_TEMPERATURE_SAVING_REWARD
            print(
                self.name + " rewarded for saving body heat when body temperature is low")

        return reward

    def get_biggest_expected_reward(self):
        # Calculate expected rewards for next step
        self.calculate_expected_rewards_for_next_step()

        # Get state with maximum possible reward for next step
        next_best_state = max(self.expected_reward_for_next_step,
                              key=self.expected_reward_for_next_step.get)

        return self.expected_reward_for_next_step[next_best_state]

    def calculate_expected_rewards_for_next_step(self):
        # If state is DIGGING next turn, expected reward is equal to amount of snow drift decrease
        self.expected_reward_for_next_step[State.DIGGING] = round(
            self.energy*DIGGING_COEFFICIENT, 2)

        print(self.name + " energy: " + str(self.energy))
        print(self.name + " body temperature: " + str(self.body_temperature))
        print(self.name + " car battery: " + str(self.car.battery_level))

        # If state is not DIGGING, there is a chance of successful exploitation of each other agent in the simulation
        self.expected_reward_for_next_step[State.NO_ACTION] = self.expected_reward_for_next_step.get(
            State.NO_ACTION, 0) + len(self.simulation.agents)*EXPLOITATION_REWARD
        self.expected_reward_for_next_step[State.TURN_ON_HEATER] = self.expected_reward_for_next_step.get(
            State.TURN_ON_HEATER, 0) + len(self.simulation.agents)*EXPLOITATION_REWARD

        # If state is NO_ACTION, expected maximum reward is snow drift decrease + energy saved reward and body heat gained reward (if applicable)
        self.expected_reward_for_next_step[State.NO_ACTION] = round(
            self.energy*DIGGING_COEFFICIENT, 2)

        if self.energy < ENERGY_SAVING_THRESHOLD:
            self.expected_reward_for_next_step[State.NO_ACTION] = self.expected_reward_for_next_step.get(
                State.NO_ACTION, 0) + ENERGY_SAVING_REWARD
        if self.body_temperature < BODY_TEMPERATURE_SAVING_THRESHOLD and self.car.battery_level > 1:
            self.expected_reward_for_next_step[State.NO_ACTION] = self.expected_reward_for_next_step.get(
                State.NO_ACTION, 0) + BODY_TEMPERATURE_SAVING_REWARD

        # If state is TURN_ON_HEATER, expected maximum reward is snow drift decrease + energy saved reward and body heat gained reward (if applicable)
        self.expected_reward_for_next_step[State.TURN_ON_HEATER] = round(
            self.energy*DIGGING_COEFFICIENT, 2)

        if self.energy < ENERGY_SAVING_THRESHOLD:
            self.expected_reward_for_next_step[State.TURN_ON_HEATER] = self.expected_reward_for_next_step.get(
                State.TURN_ON_HEATER, 0) + ENERGY_SAVING_REWARD
        if self.body_temperature < BODY_TEMPERATURE_SAVING_THRESHOLD and self.car.battery_level > 1:
            self.expected_reward_for_next_step[State.TURN_ON_HEATER] = self.expected_reward_for_next_step.get(
                State.TURN_ON_HEATER, 0) + BODY_TEMPERATURE_SAVING_REWARD

        print(self.name + " expected rewards for next step: ")
        for key, value in self.expected_reward_for_next_step.items():
            print(key, value)
