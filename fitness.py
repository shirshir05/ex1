import sys
from configparser import ConfigParser

import numpy as np
from Game import Game
from MeasureForFitness import MeasureForFitness

INIT_FITNESS = 300


class Fitness:

    def __init__(self, gen_length):
        '''
            :param gen_length= maximum number of moves allowed- set to a default value
        '''
        self.gen_length = gen_length
        self.game = Game("one_input.txt", 1)
        self.fitness = INIT_FITNESS
        self.measure = MeasureForFitness()
        self.config_object = ConfigParser()
        self.config_object.read("config.ini")
        self.Measure = self.config_object["Measure"]

    def evaluate(self, child):
        return 0


"""
    in evaluate:
        self.measure.init(self.game, child)
        function:
            # gen_length
           self.fitness -= self.measure.gen_length(self.gen_length)
           
            # is_completed
            if self.game.is_completed(level=1):
                return 0
                
            # worker_in_deadlock
            self.fitness += self.measure.worker_in_deadlock(level=1)
            
            # count_left_box
            self.fitness += self.measure.count_left_box(level=1)
            
            # euclidean_distance
            self.fitness += self.measure.euclidean_distance()
            
            # box left - Absolute distance
            range_min_difference = 0
            range_max_difference = 0
            max_difference = self.Measure["number_box"] * self.Measure["left_box"]
            abs_difference = self.measure.absolute_distance(self.measure.count_left_box(level=1),
                                                            range_min_difference, range_max_difference, max_difference)
    
            # Solution Length - Absolute distance
            range_max_length = float("inf")
            max_length = float("inf")
            range_min_length = self.Measure["len_opt_solution"]
            x = self.gen_length - len(child)
            sol_length = self.measure.absolute_distance(x, range_min_length, range_max_length, max_length)

"""


class AreaLengthFitness(Fitness):

    def __init__(self, gen_length):
        super().__init__(gen_length)
        self.measure = MeasureForFitness()

    def evaluate(self, child):
        self.measure.init(self.game, child)
        self.game.play(level=1, list_move=child)

        # This part rewards short sequences
        self.fitness -= self.measure.gen_length(self.gen_length)

        if self.game.is_completed(level=1):
            return 0,
        self.fitness += self.measure.worker_in_deadlock(level=1)
        self.fitness -= self.measure.count_left_box(level=1)
        return self.fitness,


# euclidean distance
class SimpleDistanceFitness(Fitness):

    def __init__(self, gen_length):
        super().__init__(gen_length)

    def evaluate(self, child):
        self.measure.init(self.game, child)
        self.game.play(level=1, list_move=child)
        return self.measure.euclidean_distance(),


# =======================================================================================#

# Absolute Difference & Solution Length:
class AbsDifferenceSolutionLengthFitness(Fitness):

    def __init__(self, gen_length):
        super().__init__(gen_length)

    def evaluate(self, child):
        self.measure.init(self.game, child)
        self.game.play(level=1, list_move=child)

        # box left - Absolute distance
        range_min_difference = 0
        range_max_difference = 0
        max_difference = self.Measure["number_box"] * self.Measure["left_box"]
        abs_difference = self.measure.absolute_distance(self.measure.count_left_box(level=1),
                                                        range_min_difference, range_max_difference, max_difference)

        # Solution Length - Absolute distance
        range_max_length = float("inf")
        max_length = float("inf")
        range_min_length = self.Measure["len_opt_solution"]
        x = self.gen_length - len(child)
        sol_length = self.measure.absolute_distance(x, range_min_length, range_max_length, max_length)

        return np.mean(abs_difference + sol_length),


# =======================================================================================#
# distance & Box:
class DistanceAndBox(Fitness):

    def __init__(self, gen_length):
        super().__init__(gen_length)

    def area_fitness(self):
        if self.game.is_completed(level=1):
            return 0
        self.fitness += self.measure.worker_in_deadlock(level=1)
        self.fitness -= self.measure.count_left_box(level=1)
        return self.fitness

    def evaluate(self, child):

        self.game.play(level=1, list_move=child)


        boxes_deadlock = self.game.crate_deadlock(1)

        area_f = self.area_fitness()
        euclidean_distance = self.measure.euclidean_distance()

        return area_f + euclidean_distance,
