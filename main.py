import simpy
from agents import Human  # TODO: name stuff better
from simulation import Simulation

# Run the simulation
env = simpy.Environment()
simulation = Simulation(env)

agent1 = Human(env, simulation, "Agent 1")
agent2 = Human(env, simulation, "Agent 2")
agent3 = Human(env, simulation, "Agent 3")

env.process(simulation.run(env))
env.run()
