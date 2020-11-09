
import sys
import numpy as np
import Game

class Fitness:

    def __init__(self, GENE_LENGTH):
        '''
            :param GENE_LENGTH= maximum number of moves allowed- set to a default value
        '''
        self.GENE_LENGTH = GENE_LENGTH
        self.game = Game("name_file", 1)

    def evaluate(self, child):
        return 0


# =======================================================================================#

class AreaLengthFitness(Fitness):
    '''
    – Population size: 1000
    – Generations: 100
    – Chromosome length: 20 (maximum solution length, = GENE_LENGTH)
    – Mutation rate: 0.07
    - selection- 0.95 of the population
    - crossover: one point crossover
    - 50 runs
    '''
    def __init__(self, GENE_LENGTH):
        super().__init__(GENE_LENGTH)

    def area_fitness(self, final_state):
        # a complete solution gains an absolute value of 300 for this component;
        if self.game.is_completed(final_state):
            return 300
        # if deadlock is reached (i.e., the monk is unable to move) a value of zero is awarded
        x, y = self.game.worker(final_state)
        if self.game.can_move(x, y, final_state) == False:
            return 0
        # give a
        else:
            left_crates = self.game.count_left_crates(final_state)
            return 300 - (50 * left_crates)

    def evaluate(self, child):
        final_state = self.game.play(child)
        fitness = 0
        # This part rewards short sequences
        fitness += (self.GENE_LENGTH - len(child)) * (200 / self.GENE_LENGTH)

        area_f = self.area_fitness(final_state)
        if (area_f > 0):
            fitness += (1 - area_f) * 200
        elif area_f == 300:
            fitness += 300
        else:
            fitness = 0
        return fitness


# =======================================================================================#

# euclidean distance
class SimpleDistanceFitness(Fitness):

    def __init__(self, GENE_LENGTH):
        super().__init__(GENE_LENGTH)

    def evaluate(self, child):
        final_state = self.game.play(child)

        min_distances = []
        for row in final_state.matrix:
            for cell in row:
                if cell == '$':
                    distances = []
                    for row_target in final_state.matrix:
                        for cell_target in row_target:
                            if cell_target == '.':
                                d = np.sqrt(((cell[0] - cell_target[0]) ** (cell[0] - cell_target[0]))
                                            + ((cell[1] - cell_target[1]) ** (cell[1] - cell_target[1])))
                                distances.append(d)
                    min_d = np.min(distances)
                    min_distances.append(min_d)

        return np.sum(min_distances)


# Absolute Difference & Solution Length:

class AbsDifferenceSolutionLengthFitness(Fitness):
    '''
    mutation: picks a random location from the array and replace it with another random value.
    selection: tournament selection of size 2
    population size: 500
    number of generations: 2000
    crossover rate: 70%
    mutation rate: 30%
    '''
    def __init__(self, GENE_LENGTH):
        super().__init__(GENE_LENGTH)

    def f(x, range_min, range_max, max):
        if x < range_min:
            return (range_min - x) / range_min
        elif range_min <= x <= range_max:
            return 1
        else:
            return (x - range_max) / (max - range_max)

    def evaluate(self, child):
        final_state = self.game.play(child)
        x = self.GENE_LENGTH - len(child)
        range_min_difference = 0
        range_max_difference = 0
        max_difference = 6
        range_min_length = 253
        range_max_length = sys.maxint
        max_length = sys.maxint

        abs_difference = self.f(self.game.count_left_crates(final_state),
                                range_min_difference,
                                range_max_difference,
                                max_difference)
        sol_length = self.f(x, range_min_length, range_max_length, max_length)

        return np.mean(abs_difference + sol_length)

# =======================================================================================#
# very simple fitness: (least number of moves required to solve the puzzle)

def count_left_crates(final_state):
    counter = 0
    for row in final_state.matrix:
        for cell in row:
            if cell == '$':
                counter = counter + 1
    return counter