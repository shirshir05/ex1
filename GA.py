from datetime import datetime

from deap import base, creator
import random
from deap import tools
from configparser import ConfigParser
import numpy as np
from Game import Game
from MeasureForFitness import MeasureForFitness
from fitness import SimpleDistanceFitness, AbsDifferenceSolutionLengthFitness, AreaLengthFitness, DistanceAndBox
from tqdm import tqdm
from SaveRun import SaveRun
import pickle

class GA:

    def define_init_pop_random(self):
        move_index = random.randint(0, 7)
        return self.possible_Moves[move_index]

    def write_file(self, name):
        self.write_run.write_config(name)

    def define_init_pop_from_solution(self):
        data_set_permutation = SaveRun.read_permutations()
        return random.sample(data_set_permutation, 1)[0]

    def __init__(self, file_name):
        self.write_run = SaveRun()
        self.fitness_dict = {"AreaLengthFitness": AreaLengthFitness,
                             "AbsDifferenceSolutionLengthFitness": AbsDifferenceSolutionLengthFitness,
                             "SimpleDistanceFitness": SimpleDistanceFitness,
                             "DistanceAndBox": DistanceAndBox,
                             }

        self.crossover_dict = {"cxTwoPoint": tools.cxTwoPoint,
                               "cxUniform": tools.cxUniform,
                               "cxOnePoint": tools.cxOnePoint,
                               "cxOrdered": tools.cxOrdered,
                               "cxPartialyMatched": tools.cxPartialyMatched,
                               "cxUniformPartialyMatched": tools.cxUniformPartialyMatched,
                               "cxBlend": tools.cxBlend,
                               "cxESBlend": tools.cxESBlend,
                               "cxESTwoPoint": tools.cxESTwoPoint,
                               "cxSimulatedBinary": tools.cxSimulatedBinary,
                               "cxSimulatedBinaryBounded": tools.cxSimulatedBinaryBounded,
                               "cxMessyOnePoint": tools.cxMessyOnePoint}
        self.mutate_dict = {"mutShuffleIndexes": tools.mutShuffleIndexes,
                            "mutFlipBit": tools.mutFlipBit,
                            "mutPolynomialBounded": tools.mutPolynomialBounded,
                            "mutUniformInt": tools.mutUniformInt,
                            "mutESLogNormal": tools.mutESLogNormal}

        self.config_object = ConfigParser()
        self.file_name = file_name
        self.config_object.read(file_name)
        # params
        self.params = self.config_object["PARAMS"]
        self.size_population_init = int(self.params["size_population_init"])
        self.size_feature = int(self.params["size_feature"])  # size_feature >= 253
        self.seed_number = float(self.params["seed_number"])
        self.number_run = int(self.params["number_run"])
        self.permutations = self.params.getboolean("permutations")

        # probs
        self.probs = self.config_object["PROBS"]
        self.cross_over_prob = float(self.probs["cross_over_prob"])
        self.mutation_prob = float(self.probs["mutation_prob"])

        # operators
        self.operators = self.config_object["OPERATORS"]
        self.fitness = self.fitness_dict[self.operators["fitness"]](self.size_feature, file_name)
        self.crossover = self.crossover_dict[self.operators["mate"]]
        self.mutate = self.mutate_dict[self.operators["mutate"]]
        # endregion

        self.possible_Moves = ['U', 'R', 'L', 'D', 'u', 'r', 'l', 'd']
        random.seed(self.seed_number)

        creator.create("FitnessMin", base.Fitness, weights=(-1.0,))
        creator.create("Individual", list, fitness=creator.FitnessMin)
        self.write_file(file_name)
        self.toolbox = base.Toolbox()

        if self.permutations:
            self.toolbox.register("random_sampling", self.define_init_pop_from_solution)
            self.toolbox.register("individual", tools.initIterate, creator.Individual, self.toolbox.random_sampling)

        else:
            self.toolbox.register("attr_str", self.define_init_pop_random)
            self.toolbox.register("individual", tools.initRepeat, creator.Individual, self.toolbox.attr_str,
                                  n=self.size_feature)

        self.toolbox.register("population", tools.initRepeat, list, self.toolbox.individual)

        # region define operator
        self.toolbox.register("mate", self.crossover)
        # self.toolbox.register("mutate", self.mutate_rand, indpb=self.mutation_prob)
        self.toolbox.register("mutate", self.mutate, indpb=self.mutation_prob)
        self.toolbox.register("select", tools.selTournament, tournsize=5)
        self.toolbox.register("evaluate", self.fitness.evaluate)

    def mutate_rand(self, individual, indpb):
        size = len(individual)
        for i in range(size):
            if random.random() < indpb:
                individual[i] = self.define_init_pop_random()
        return individual,

    def evaluate_inv(self, inv):
        measure = MeasureForFitness()
        game = Game("one_input.txt", 1)
        measure.init(game, inv, self.file_name)
        game.play(level=1, list_move=inv)

        with open(str("inv") + '.txt', 'a') as filehandle:
            filehandle.write(' %d,' % measure.box_deadlock(1))
            filehandle.write(' %d,' % measure.euclidean_distance('.', False))
            filehandle.write(' %d,' % measure.box_on_the_way())
            filehandle.write(' %s,' % game.is_completed(level=1))
            filehandle.write('%d,' % measure.worker_in_deadlock(level=1))
            filehandle.write('%d \n' % measure.count_left_box(level=1))

    def main(self):
        min_inv = None
        time = datetime.now()
        gen_time = []
        pop = self.toolbox.population(n=self.size_population_init)
        stats = tools.Statistics(lambda ind: ind.fitness.values)
        stats.register("avg", np.mean)
        stats.register("std", np.std)
        stats.register("min", np.min)
        stats.register("max", np.max)
        stats.register("med",np.median)

        logbook = tools.Logbook()
        logbook.header = ["gen", "evals"] + stats.fields

        # print(pop)
        # Evaluate the entire population
        fitnesses = map(self.toolbox.evaluate, pop)
        min_fitness = float("inf")
        sum = 0
        for ind, fit in zip(pop, fitnesses):
            ind.fitness.values = fit
            sum += fit[0]
            if fit[0] < min_fitness:
                min_fitness = fit[0]
        self.write_run.write_epoch(-1, min_fitness, sum, self.size_population_init)

        for epoch in tqdm(range(self.number_run)):
            # Select the next generation individuals
            offspring = self.toolbox.select(pop, len(pop))
            # Clone the selected individuals
            offspring = list(map(self.toolbox.clone, offspring))

            min_fitness = float("inf")
            sum_fitness = 0

            # Apply crossover and mutation on the offspring
            for child1, child2 in zip(offspring[::2], offspring[1::2]):
                if random.random() < self.cross_over_prob:
                    self.toolbox.mate(child1, child2)
                    del child1.fitness.values
                    del child2.fitness.values

            for mutant in offspring:
                if random.random() < self.mutation_prob:
                    self.toolbox.mutate(mutant)
                    del mutant.fitness.values

            # Evaluate the individuals with an invalid fitness
            invalid_ind = [ind for ind in offspring if not ind.fitness.valid]
            # invalid_ind = [ind for ind in offspring]
            fitnesses = map(self.toolbox.evaluate, invalid_ind)
            for ind, fit in zip(invalid_ind, fitnesses):
                ind.fitness.values = fit


            for ind in offspring:
                sum_fitness += ind.fitness.values[0]
                if min_fitness > ind.fitness.values[0]:
                    min_fitness = ind.fitness.values[0]
                    min_inv = ind

            #self.write_run.write_epoch(epoch, min_fitness, sum_fitness, self.size_population_init)

            # The population is entirely replaced by the offspring
            pop[:] = offspring
            # for part in pop:
            #    self.toolbox.update(pop)  # min_ind = best

            # Gather all the fitnesses in one list and print the stats
            self.evaluate_inv(min_inv)
            logbook.record(gen=epoch, evals=len(pop), **stats.compile(pop))
            #print(logbook.stream)
            gen_time.append(time.minute-datetime.now().minute)
            time = datetime.now()
        # print(pop)
        pickle.dump(logbook, open("logbook", 'wb'))
        print("AVG generation runtime = {}".format(np.mean(gen_time)))
        print(min_inv)
        return pop


try:
    ga = GA("config.ini")
    ga.main()
except Exception as e:
    print(e)
    pass

# try:
#
#     ga = GA("1B.ini")
#     ga.main()
# except Exception as e:
#     print(e)
#     pass
#
# try:
#     ga = GA("1C.ini")
#     ga.main()
# except Exception as e:
#     print(e)
#     pass

# try:
#     ga1 = GA("1D.ini")
#     ga1.main()
# except Exception as e:
#     print(e)
#     pass
#
# try:
#     ga2 = GA("1E.ini")
#     ga2.main()
# except Exception as e:
#     print(e)
#     pass

# try:
#     ga3 = GA("1F.ini")
#     ga3.main()
# except Exception as e:
#     pass

# try:
#     ga = GA("2A.ini")
#     ga.main()
# except Exception as e:
#     pass
#
# try:
#     ga = GA("2B.ini")
#     ga.main()
# except Exception as e:
#     pass
#
# try:
#     ga = GA("2C.ini")
#     ga.main()
# except Exception as e:
#     pass
#
# try:
#     ga = GA("2D.ini")
#     ga.main()
# except Exception as e:
#     pass
#
# try:
#     ga = GA("2E.ini")
#     ga.main()
# except Exception as e:
#     pass
#
# try:
#     ga = GA("2F.ini")
#     ga.main()
# except Exception as e:
#     pass
#
# try:
#     ga = GA("3A.ini")
#     ga.main()
# except Exception as e:
#     pass
#
# try:
#     ga = GA("3B.ini")
#     ga.main()
# except Exception as e:
#     pass
# try:
#     ga = GA("3C.ini")
#     ga.main()
# except Exception as e:
#     pass
#
# try:
#     ga = GA("3D.ini")
#     ga.main()
# except Exception as e:
#     pass
#
# try:
#     ga = GA("3E.ini")
#     ga.main()
# except Exception as e:
#     pass
#
# try:
#     ga = GA("3F.ini")
#     ga.main()
# except Exception as e:
#     pass
