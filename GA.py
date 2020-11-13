from deap import base, creator
import random
from deap import tools
from configparser import ConfigParser
from fitness import SimpleDistanceFitness, AbsDifferenceSolutionLengthFitness, AreaLengthFitness, DistanceAndBox
from tqdm import tqdm
from SaveRun import SaveRun

# region write run parameter
write_run = SaveRun()
write_run.write_config()
# endregion

# region define dict for fitness, crossover, mutate

fitness_dict = {"AreaLengthFitness": AreaLengthFitness,
                "AbsDifferenceSolutionLengthFitness": AbsDifferenceSolutionLengthFitness,
                "SimpleDistanceFitness": SimpleDistanceFitness,
                "DistanceAndBox": DistanceAndBox}

crossover_dict = {"cxTwoPoint": tools.cxTwoPoint,
                  "cxUniform": tools.cxUniform}

mutate_dict = {"mutShuffleIndexes": tools.mutShuffleIndexes}
crossover_dict = {"cxTwoPoint": tools.cxTwoPoint}
mutate_dict = {"mutShuffleIndexes": tools.mutShuffleIndexes}
# endregion

# region Read config.ini file and write parameter(params, probs, operators)
config_object = ConfigParser()
config_object.read("config.ini")
# params
params = config_object["PARAMS"]
size_population_init = int(params["size_population_init"])
size_feature = int(params["size_feature"])  # size_feature >= 253
seed_number = float(params["seed_number"])
number_run = int(params["number_run"])
permutations = params.getboolean("permutations")

# probs
probs = config_object["PROBS"]
cross_over_prob = float(probs["cross_over_prob"])
mutation_prob = float(probs["mutation_prob"])

# operators
operators = config_object["OPERATORS"]
fitness = fitness_dict[operators["fitness"]](size_feature)
crossover = crossover_dict[operators["mate"]]
mutate = mutate_dict[operators["mutate"]]
######## I didnt cange the select in the code itself. it has another different param for each method
# endregion

possible_Moves = ['U', 'R', 'L', 'D', 'u', 'r', 'l', 'd']
random.seed(seed_number)

creator.create("FitnessMin", base.Fitness, weights=(-1.0,))
creator.create("Individual", list, fitness=creator.FitnessMin)


def mutate_rand(individual, indpb):
    size = len(individual)
    for i in range(size):
        if random.random() < indpb:
            individual[i] = define_init_pop_random()
    return individual,


# region init pop
def define_init_pop_random():
    move_index = random.randint(0, 7)
    return possible_Moves[move_index]


def define_init_pop_from_solution():
    data_set_permutation = SaveRun.read_permutations()
    return random.sample(data_set_permutation, 1)[0]
# endregion


toolbox = base.Toolbox()

if permutations:
    toolbox.register("random_sampling", define_init_pop_from_solution)
    toolbox.register("individual", tools.initIterate, creator.Individual, toolbox.random_sampling)

else:
    toolbox.register("attr_str", define_init_pop_random)
    toolbox.register("individual", tools.initRepeat, creator.Individual, toolbox.attr_str, n=size_feature)

toolbox.register("population", tools.initRepeat, list, toolbox.individual)

# region define operator
toolbox.register("mate", crossover)
toolbox.register("mutate", mutate_rand, indpb=mutation_prob)
toolbox.register("select", tools.selTournament, tournsize=5)
toolbox.register("evaluate", fitness.evaluate)


# endregion


def main():
    pop = toolbox.population(n=size_population_init)
    # print(pop)
    # Evaluate the entire population
    fitnesses = map(toolbox.evaluate, pop)
    min_fitness = float("inf")
    sum = 0
    for ind, fit in zip(pop, fitnesses):
        ind.fitness.values = fit
        sum += fit[0]
        if fit[0] < min_fitness:
            min_fitness = fit[0]
            print(min_fitness)
    write_run.write_epoch(-1, min_fitness, sum, size_population_init)

    for epoch in tqdm(range(number_run)):
        # Select the next generation individuals
        offspring = toolbox.select(pop, len(pop))
        # Clone the selected individuals
        offspring = list(map(toolbox.clone, offspring))

        min_fitness = float("inf")
        sum_fitness = 0

        # Apply crossover and mutation on the offspring
        for child1, child2 in zip(offspring[::2], offspring[1::2]):
            if random.random() < cross_over_prob:
                toolbox.mate(child1, child2)
                del child1.fitness.values
                del child2.fitness.values
            else:
                sum_fitness += child1.fitness.values[0]
                sum_fitness += child2.fitness.values[0]
                if min_fitness > child1.fitness.values[0]:
                    min_fitness = child1.fitness.values[0]
                if min_fitness > child2.fitness.values[0]:
                    min_fitness = child2.fitness.values[0]

        for mutant in offspring:
            if random.random() < mutation_prob:
                toolbox.mutate(mutant)
                del mutant.fitness.values

        # Evaluate the individuals with an invalid fitness
        invalid_ind = [ind for ind in offspring if not ind.fitness.valid]
        # invalid_ind = [ind for ind in offspring]
        fitnesses = map(toolbox.evaluate, invalid_ind)
        for ind, fit in zip(invalid_ind, fitnesses):
            ind.fitness.values = fit
            sum_fitness += ind.fitness.values[0]

        for ind in offspring:
            if min_fitness > ind.fitness.values[0]:
                min_fitness = ind.fitness.values[0]

        write_run.write_epoch(epoch, min_fitness, sum_fitness, size_population_init)

        # The population is entirely replaced by the offspring
        pop[:] = offspring
    # print(pop)
    return pop


main()
