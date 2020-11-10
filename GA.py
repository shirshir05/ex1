# region import
import itertools

from deap import base, creator
import random
from deap import tools
from configparser import ConfigParser

from fitness import SimpleDistanceFitness, AbsDifferenceSolutionLengthFitness, AreaLengthFitness, Fitness,DistanceAndCrates




from SaveRun import SaveRun
from fitness import SimpleDistanceFitness, AbsDifferenceSolutionLengthFitness, AreaLengthFitness, Fitness

# endregion

# region write run parameter todo remove comment
# write_run = SaveRun()
# write_run.write_config()
# endregion

# region define dict for fitness, crossover, mutate

fitness_dict = {"AreaLengthFitness": AreaLengthFitness,
                "AbsDifferenceSolutionLengthFitness": AbsDifferenceSolutionLengthFitness,
                "SimpleDistanceFitness": SimpleDistanceFitness,
                "DistanceAndCrates": DistanceAndCrates}

crossover_dict = {"cxTwoPoint": tools.cxTwoPoint,
                  "cxTwoPoint":tools.cxTwoPoint,
                  "cxUniform":tools.cxUniform}

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
permutations = params["permutations"]

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
            individual[i] = random_pop()
    return individual,

def random_pop():
    move_index = random.randint(0, 7)
    return possible_Moves[move_index]

def define_init_pop():
    if permutations:
        data_set_permutation = SaveRun.read_permutations()
        random_permutation = random.sample(data_set_permutation, size_population_init)
        return random_permutation


toolbox = base.Toolbox()

if permutations == 'True':
    toolbox.register("random_sampling", random.sample, define_init_pop, 1)
    toolbox.register("individual", tools.initRepeat, creator.Individual, toolbox.random_sampling, n=size_feature)

else:
    toolbox.register("attr_str", random_pop)
    toolbox.register("individual", tools.initRepeat, creator.Individual, toolbox.attr_str, n=size_feature)

toolbox.register("population", tools.initRepeat, list, toolbox.individual)

# define operator
toolbox.register("mate", tools.cxMessyOnePoint)
toolbox.register("mutate", mutate, indpb=0.4)

toolbox.register("select", tools.selTournament, tournsize=5)
# region define operator
toolbox.register("mate", crossover)
toolbox.register("mutate", mutate, indpb=mutation_prob)
toolbox.register("select", tools.selTournament, tournsize=2)
toolbox.register("evaluate", fitness.evaluate)
# endregion


def main():
    pop = toolbox.population(n=size_population_init)
    #print(pop)
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
            print(fit)

        # The population is entirely replaced by the offspring
        pop[:] = offspring
    # print(pop)
    return pop


main()
