import simpy
from agents import Human, Car
from simulation import Simulation

# TODO: step function, output goal reached/agent dead, increment iteration

# Setup
# TODO: what are the parameters?


# Run the simulation
env = simpy.Environment()
simulation = Simulation(env)

agent1 = Human(env, simulation, "Agent 1")
agent2 = Human(env, simulation, "Agent 2")

env.process(simulation.run(env))
env.run()

# View the results
# TODO: What is the simulation output, what statistics should be gathered?
