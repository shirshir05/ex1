from configparser import ConfigParser

from pandas import np


class MeasureForFitness:

    def __init__(self):
        self.config_object = ConfigParser()
        self.individual = None
        self.game = None
        self.Measure = None

    def init(self, game, individual):
        self.individual = individual
        self.game = game
        self.config_object.read("config.ini")
        self.Measure = self.config_object["Measure"]

    def position(self, level):
        """
           return position of boxes,free cell, dock and worker
       """
        list_box = []
        list_free = []
        list_dock = []
        worker = None
        for row in self.game.matrix[level - 1]:
            for col in row:
                if col == "$":
                    list_box.append((row, col))
                elif col == " ":
                    list_free.append((row, col))
                elif col == "*" or col == "." or "+":
                    list_dock.append((row, col))
                elif col == "@" or col == "+":
                    worker = (row, col)
        return list_box, list_free, list_dock, worker

    def gen_length(self, gen_length):
        """
            This measure considering the size of the solution
        """
        x = (gen_length - len(self.individual))
        y = (int(self.Measure["div_in_gen_length"]) / gen_length)
        return x * y

    def worker_in_deadlock(self, level):
        """
            :Return
                worker_in_deadlock - if worker in deadlock
                o - otherwise
         """
        if not self.game.can_move(level, 0, -1) and not self.game.can_move(level, 0, 1):
            if not self.game.can_move(level, -1, 0) and not self.game.can_move(level, 1, 0):
                return self.Measure["worker_in_deadlock"]
        else:
            return 0

    def count_left_box(self, level):
        """
           :Return
               (The number of boxes out of place) * left_box
        """
        counter = 0
        for row in self.game.matrix[level - 1]:
            for cell in row:
                if cell == '$':
                    counter = counter + 1
        return self.Measure["left_box"] * counter

    def euclidean_distance(self):
        """
            :Return
                The minimum distance for box from the dock * self.Measure["euclidean_distance"]
        """
        min_distances = []
        row_pos = -1
        for row in self.game.matrix[0]:
            row_pos = row_pos + 1
            col_pos = -1
            for cell in row:
                col_pos = col_pos + 1
                if cell == '$':
                    distances = []
                    target_row_pos = -1
                    for row_target in self.game.matrix[0]:
                        target_row_pos = target_row_pos + 1
                        target_col_pos = -1
                        for cell_target in row_target:
                            target_col_pos = target_col_pos + 1
                            if cell_target == '.':
                                d = np.sqrt(((row_pos - target_row_pos) ** 2) + ((col_pos - target_col_pos) ** 2))
                                distances.append(d)
                    min_d = np.min(distances)
                    min_distances.append(min_d)
        return self.Measure["euclidean_distance"] * np.sum(min_distances)

    def absolute_distance(self, x_val, range_min, range_max, max):
        """
            (x_val - range_max) / (max - range_max)
        """
        if x_val < range_min:
            return (range_min - x_val) / range_min
        elif range_min <= x_val <= range_max:
            return 1
        else:
            return (x_val - range_max) / (max - range_max)


