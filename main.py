import simpy
from agents import Agent, SlightlySmarterAgent
from simulation import Simulation

# Run the simulation
env = simpy.Environment()
simulation = Simulation(env)

agent1 = Agent(env, simulation, "Agent 1")
agent2 = Agent(env, simulation, "Agent 2")
agent3 = Agent(env, simulation, "Agent 3")
# TODO: experiments with same type and different agents (homogeneous and hetergeneous agents)
agent4 = Agent(env, simulation, "Agent 4")


env.process(simulation.run(env))
env.run()
# show standard deviation and mean estimation in randomized behaviour
