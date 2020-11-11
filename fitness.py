import sys
import numpy as np
from Game import Game


class Fitness:

    def __init__(self, GENE_LENGTH):
        '''
            :param GENE_LENGTH= maximum number of moves allowed- set to a default value
        '''
        self.GENE_LENGTH = GENE_LENGTH
        self.game = Game("one_input.txt", 1)

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

    def area_fitness(self):
        # a complete solution gains an absolute value of 0 for this component;
        if self.game.is_completed(level=1):
            return 0
        # if deadlock is reached (i.e., the monk is unable to move) a value of 300 is awarded
        row, col, pos = self.game.worker(level=1)
        if self.game.is_deadlock_player(level=1):
            # print("deadlock")
            return 300
        # give a
        else:
            left_crates = self.game.count_left_crates(level=1)
            # if left_crates==6:
            #     print("all crates left")
            return (50 * left_crates)

    def evaluate(self, child):
        # if self.game.play(level=1, list_move=child) == -1:
        #     # return fitness=0 in case that child's moves are not legal
        #     return 0,
        self.game.play(level=1, list_move=child)
        fitness = 300
        # This part rewards short sequences
        fitness -= (self.GENE_LENGTH - len(child)) * (200 / self.GENE_LENGTH)

        area_f = self.area_fitness()
        if area_f == 300:
            fitness += 300
        elif (area_f > 0):
            fitness -= (1 - area_f) * 200
        else:
            fitness = 0
        return fitness,


# =======================================================================================#

# euclidean distance
class SimpleDistanceFitness(Fitness):

    def __init__(self, GENE_LENGTH):
        super().__init__(GENE_LENGTH)

    def evaluate(self, child):
        self.game.play(level=1, list_move=child)
        min_distances = []
        row_pos = 0
        for row in self.game.matrix[0]:
            row_pos = row_pos + 1
            col_pos = 0
            for cell in row:
                col_pos = col_pos + 1
                if cell == '$':
                    distances = []
                    target_row_pos = 0
                    for row_target in self.game.matrix[0]:
                        target_row_pos = target_row_pos + 1
                        target_col_pos = 0
                        for cell_target in row_target:
                            target_col_pos = target_col_pos + 1
                            if cell_target == '.':
                                d = np.sqrt(((row_pos - target_row_pos) ** 2) + ((col_pos - target_col_pos) ** 2))
                                distances.append(d)
                    min_d = np.min(distances)
                    min_distances.append(min_d)

        return np.sum(min_distances),


# =======================================================================================#

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

    def f(self, x_val, range_min, range_max, max):
        if x_val < range_min:
            return (range_min - x_val) / range_min
        elif range_min <= x_val <= range_max:
            return 1
        else:
            return (x_val - range_max) / (max - range_max)

    def evaluate(self, child):
        # if self.game.play(level=1, list_move=child) == -1:
        #     # return fitness=0 in case that child's moves are not legal
        #     return 0
        self.game.play(level=1, list_move=child)
        range_min_difference = 0
        range_max_difference = 0
        max_difference = 6
        range_min_length = 253
        range_max_length = float("inf")
        max_length = float("inf")
        x = self.GENE_LENGTH - len(child)
        abs_difference = self.f(self.game.count_left_crates(level=1), range_min_difference, range_max_difference,
                                max_difference)
        sol_length = self.f(x, range_min_length, range_max_length, max_length)

        return np.mean(abs_difference + sol_length),


# =======================================================================================#
# distance & crates:
class DistanceAndCrates(Fitness):

    def __init__(self, GENE_LENGTH):
        super().__init__(GENE_LENGTH)

    def sum_distance(self):
        min_distances = []
        row_pos = 0
        for row in self.game.matrix[0]:
            row_pos = row_pos + 1
            col_pos = 0
            for cell in row:
                col_pos = col_pos + 1
                if cell == '$':
                    distances = []
                    target_row_pos = 0
                    for row_target in self.game.matrix[0]:
                        target_row_pos = target_row_pos + 1
                        target_col_pos = 0
                        for cell_target in row_target:
                            target_col_pos = target_col_pos + 1
                            if cell_target == '.':
                                d = np.sqrt(((row_pos - target_row_pos) ** 2) + ((col_pos - target_col_pos) ** 2))
                                distances.append(d)
                    min_d = np.min(distances)
                    min_distances.append(min_d)
        return np.sum(min_distances)

    def area_fitness(self):
        # a complete solution gains an absolute value of 0 for this component;
        if self.game.is_completed(level=1):
            return 0
        # if deadlock is reached (i.e., the monk is unable to move) a value of 300 is awarded
        if self.game.is_deadlock_player(level=1):
            # print("deadlock")
            return 300
        # give a
        else:
            left_crates = self.game.count_left_crates(level=1)
            # if left_crates==6:
            #     print("all crates left")
            return (50 * left_crates)

    def evaluate(self, child):

        self.game.play(level=1, list_move=child)


        boxes_deadlock = self.game.crate_deadlock(1)

        area_f = self.area_fitness()
        dis = self.sum_distance()

        return area_f + dis ,


# =======================================================================================#

if __name__ == '__main__':
    string = "ullluuuLUllDlldddrRRRRRRRRRRRRurDllllllllllllllulldRRRRRRRRRRRRRdrUluRRlldlllllluuululldDDuulldddrRR RRRRRRRRRRlllllllluuulLulDDDuulldddrRRRRRRRRRRRurDlllllllluuululuurDDllddddrrruuuLLulDDDuulldddrRRRRRRRRRRdrUluRldlllllluuuluuullDDDDDuulldddrRRRRRRRRRRR"
    fitness = DistanceAndCrates(len(string))
    print(fitness.evaluate(string)[0])
