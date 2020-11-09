from deap import base, creator
import random
from deap import tools

possible_Moves = ['U', 'R', 'L', 'D', 'u', 'r', 'l', 'd']
size_population_init = 10
# size_feature >= 253
size_feature = 10
seed_number = 0.5
random.seed(seed_number)
cross_over_prob = 0.5
mutation_prob = 0.5
number_run= 500


creator.create("FitnessMin", base.Fitness, weights=(-1.0,))
creator.create("Individual", list, fitness=creator.FitnessMin)


def random_pop():
    move_index = random.randint(0, 7)
    return possible_Moves[move_index]

toolbox = base.Toolbox()
toolbox.register("attr_str", random_pop)
toolbox.register("individual", tools.initRepeat, creator.Individual,
                 toolbox.attr_str, n=size_feature)
toolbox.register("population", tools.initRepeat, list, toolbox.individual)

# define fitness
def evaluate(individual):
    return 0,


# define operator
toolbox.register("mate", tools.cxTwoPoint)
toolbox.register("mutate", tools.mutShuffleIndexes, indpb=0.5)
toolbox.register("select", tools.selTournament, tournsize=3)
toolbox.register("evaluate", evaluate)


def main():
    pop = toolbox.population(n=size_population_init)

    # Evaluate the entire population
    fitnesses = map(toolbox.evaluate, pop)
    for ind, fit in zip(pop, fitnesses):
        ind.fitness.values = fit

    for g in range(number_run):
        # Select the next generation individuals
        offspring = toolbox.select(pop, len(pop))
        # Clone the selected individuals
        offspring = list(map(toolbox.clone, offspring))

        # Apply crossover and mutation on the offspring
        for child1, child2 in zip(offspring[::2], offspring[1::2]):
            if random.random() < cross_over_prob:
                toolbox.mate(child1, child2)
                del child1.fitness.values
                del child2.fitness.values

        for mutant in offspring:
            if random.random() < mutation_prob:
                toolbox.mutate(mutant)
                del mutant.fitness.values

        # Evaluate the individuals with an invalid fitness
        invalid_ind = [ind for ind in offspring if not ind.fitness.valid]
        fitnesses = map(toolbox.evaluate, invalid_ind)
        for ind, fit in zip(invalid_ind, fitnesses):
            ind.fitness.values = fit

        # The population is entirely replaced by the offspring
        pop[:] = offspring
    print(pop)
    return pop


main()