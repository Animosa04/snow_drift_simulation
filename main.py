import simpy
from agents import Agent, EpsilonGreedyAgent, QLearningAgent
from simulation import Simulation

# show standard deviation and mean estimation in randomized behaviour


def random_agent_experiment(seed):
    filename = "random_agent"

    # Run the simulation
    env = simpy.Environment()
    simulation = Simulation(env, filename)

    # One random agent
    agent1 = Agent(env, simulation, "Agent 1", seed)

    env.process(simulation.run(env))
    env.run()


def random_agents_experiment(seed):
    filename = "random_agents"

    # Run the simulation
    env = simpy.Environment()
    simulation = Simulation(env, filename)

    # Multiple random agents
    agent1 = Agent(env, simulation, "Agent 1", seed)
    agent2 = Agent(env, simulation, "Agent 2", seed)
    agent3 = Agent(env, simulation, "Agent 3", seed)
    agent4 = Agent(env, simulation, "Agent 4", seed)

    env.process(simulation.run(env))
    env.run()


def epsilon_greedy_agent_experiment(seed):
    filename = "epsilon_greedy_agent"

    # Run the simulation
    env = simpy.Environment()
    simulation = Simulation(env, filename)

    # One epsilon-greedy agents
    agent1 = EpsilonGreedyAgent(env, simulation, "Agent 1", seed)

    env.process(simulation.run(env))
    env.run()


def epsilon_greedy_agents_experiment(seed):
    filename = "epsilon_greedy_agents"

    # Run the simulation
    env = simpy.Environment()
    simulation = Simulation(env, filename)

    # Multiple epsilon-greedy agents
    agent1 = EpsilonGreedyAgent(env, simulation, "Agent 1", seed)
    agent2 = EpsilonGreedyAgent(env, simulation, "Agent 2", seed)
    agent3 = EpsilonGreedyAgent(env, simulation, "Agent 3", seed)
    agent4 = EpsilonGreedyAgent(env, simulation, "Agent 4", seed)

    env.process(simulation.run(env))
    env.run()


def qlearning_agent_experiment(seed):
    filename = "q_learning_agent"

    # Run the simulation
    env = simpy.Environment()
    simulation = Simulation(env, filename)

    # One Q-learning agent
    agent1 = QLearningAgent(env, simulation, "Agent 1", seed)

    env.process(simulation.run(env))
    env.run()


def qlearning_agents_experiment():
    # Run the simulation
    env = simpy.Environment()
    simulation = Simulation(env)

    # Multiple Q-learning agents
    agent1 = QLearningAgent(env, simulation, "Agent 1", 1)
    agent2 = QLearningAgent(env, simulation, "Agent 2", 1)
    agent3 = QLearningAgent(env, simulation, "Agent 3", 1)
    agent4 = QLearningAgent(env, simulation, "Agent 4", 1)

    env.process(simulation.run(env))
    env.run()


def heterogeneous_agents_experiment():
    # Run the simulation
    env = simpy.Environment()
    simulation = Simulation(env)

    # Q-learning agents
    agent1 = QLearningAgent(env, simulation, "Agent 1", 1)
    agent2 = QLearningAgent(env, simulation, "Agent 2", 1)

    # Random agents
    agent3 = Agent(env, simulation, "Agent 3", 1)
    agent4 = Agent(env, simulation, "Agent 4", 1)

    env.process(simulation.run(env))
    env.run()


# random_agent_experiment()
# random_agents_experiment()
# epsilon_greedy_agent_experiment()
# epsilon_greedy_agents_experiment()
# qlearning_agent_experiment()
# qlearning_agents_experiment()
# heterogeneous_agents_experiment()

for seed in range(4):
    qlearning_agent_experiment(seed)
