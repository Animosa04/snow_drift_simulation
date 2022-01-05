import simpy
from monitor import Monitor
from parameters import *
from agents import State, EpsilonGreedyAgent, QLearningAgent
import pandas as pd
import numpy as np
import datetime
import time


class Simulation(object):
    def __init__(self, env, filename):
        self.snow_drift = simpy.Container(
            env, init=SNOW_DRIFT_SIZE)
        self.agents = []
        self.time_elapsed = 0.0
        self.steps = 0
        self.monitor = Monitor(self, filename)

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
        while not self.goal_reached() and not self.all_agents_dead():
            yield env.process(self.step(env))
        end = time.time()
        self.time_elapsed = end - start
        self.monitor.make_metadata()
        self.monitor.save_simulation_data()

    def step(self, env):
        step = env.now
        snow_drift_before = self.snow_drift.level

        # For each agent that is alive

        for agent in self.agents:
            if agent.is_alive():
                # Decide what to do
                yield env.process(agent.decide_what_to_do())
                # If the decision was to dig but there is no energy left, make another decision
                while agent.state == State.DIGGING and agent.energy == 0:
                    yield env.process(agent.decide_what_to_do())
                # If the decision was to turn on heating but there is no car battery left, make another decision
                while agent.state == State.TURN_ON_HEATER and agent.car.battery_level <= 0:
                    yield env.process(agent.decide_what_to_do())
            else:
                agent.state = State.NO_ACTION

        for agent in self.agents:
            if agent.is_alive() and not self.goal_reached():
                # Update agent
                yield env.process(agent.update_agent())

                # Update snow drift
                if(agent.state == State.DIGGING):
                    if(agent.energy > 0):
                        snow_shoveled = round(
                            agent.energy*DIGGING_COEFFICIENT, 2)
                        if(snow_shoveled >= self.snow_drift.level):
                            self.snow_drift.get(self.snow_drift.level)
                        else:
                            self.snow_drift.get(snow_shoveled)

            # Log actions and results of actions
            self.monitor.append_to_result(agent, step, self.snow_drift)

        # Calculate how much snow was cleared
        snow_shoveled_in_step = snow_drift_before - self.snow_drift.level
        print("Snow drift cleared: " + str(snow_shoveled_in_step))
        print("Snow drift left: " + str(self.snow_drift.level))

        for agent in self.agents:
            if agent.is_alive() and isinstance(agent, EpsilonGreedyAgent):
                # Calculate reward for action for epsilon greedy agents
                yield env.process(agent.reward_for_step(snow_shoveled_in_step))
            if agent.is_alive() and isinstance(agent, QLearningAgent):
                # Update agent's Q-table for Q-learning agents
                yield env.process(agent.update_q_table(snow_shoveled_in_step))

        print("\n")

        self.steps += 1
        yield env.timeout(1)
