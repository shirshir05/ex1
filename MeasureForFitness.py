from configparser import ConfigParser

import numpy as np


class MeasureForFitness:

    def __init__(self):
        self.config_object = ConfigParser()
        self.individual = None
        self.game = None
        self.Measure = None

    def init(self, game, individual, name):
        self.individual = individual
        self.game = game
        self.config_object.read(name)
        self.Measure = self.config_object["Measure"]

    def position(self, level):
        """
           return position of boxes,free cell, dock and worker
       """
        list_box = []
        list_free = []
        list_dock = []
        worker = None
        index_row = 0
        for row in self.game.matrix[level - 1]:
            index_col = 0
            for col in row:
                if col == "$":
                    list_box.append((index_row, index_col))
                elif col == " ":
                    list_free.append((index_row, index_col))
                elif col == "*" or col == "." or "+":
                    list_dock.append((index_row, index_col))
                elif col == "@" or col == "+":
                    worker = (index_row, index_col)
                index_col += 1
            index_row += 1
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
                return int(self.Measure["worker_in_deadlock"])
            else:
                return 0
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
        return int(self.Measure["left_box"]) * counter

    def euclidean_distance(self, from_box, sum):
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
                            if cell_target == from_box:
                                d = np.sqrt(((row_pos - target_row_pos) ** 2) + ((col_pos - target_col_pos) ** 2))
                                distances.append(d)
                    min_d = np.min(distances)
                    if min_d != 0:
                        min_distances.append(min_d)
        if sum == True:
            score = np.sum(min_distances)
        else:
            score = np.min(min_distances)

        return int(self.Measure["euclidean_distance"]) * score

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

    def box_deadlock(self, level):
        """
            :Return
                The number box in deadlock
        """
        counter = 0
        ind_row = 0
        for row in self.game.matrix[level - 1]:
            ind_col = 0
            for cell in row:
                if cell == '$':
                    # right top corner
                    if row[ind_col + 1] in ['#', '*', '$'] and self.game.matrix[level - 1][ind_row - 1][ind_col] in [
                        '#', '*', '$']:
                        counter = counter + 1
                    # left top corner
                    if (row[ind_col - 1] in ['#', '*', '$'] and self.game.matrix[level - 1][ind_row - 1][ind_col] in [
                        '#', '*', '$']):
                        counter = counter + 1
                    # right bottom corner
                    if (row[ind_col - 1] in ['#', '*', '$'] and self.game.matrix[level - 1][ind_row + 1][ind_col] in [
                        '#', '*', '$']):
                        counter = counter + 1
                    # right bottom corner
                    if (row[ind_col + 1] in ['#', '*', '$'] and self.game.matrix[level - 1][ind_row + 1][ind_col] in [
                        '#', '*', '$']):
                        counter = counter + 1
                ind_col = ind_col + 1
            ind_row = ind_row + 1
        return int(self.Measure["box_deadlock"]) * counter

    def box_on_the_way(self):
        counter = 0
        list_box, list_free, list_dock, worker = self.position(1)
        for box in list_box:
            # if box[0] < 2:
            #     counter -= 0.5
            # if box[0] > 6 and box[0] < 8 and box[1] > 4:
            #     counter += 0.5
            if box[0] > 5 and box[1] > 8:
                counter += 1
            # if box[0] > 6 and box[1] > 14:
            #     counter += 1.5
            # if box[0] == 4 and box[1] >6:
            #     counter -= 0.5
            # if box[0] > 6 and box[1] < 4:
            #     counter -= 0.5

        return int(self.Measure["box_on_the_way"]) * counter

    def boxes_left_side(self):
        counter = 0
        list_box, list_free, list_dock, worker = self.position(1)
        for box in list_box:

            if box[0] > 6 and box[1] > 4 and box[1] < 8:
                counter += 0.5
            if box[0] > 6 and box[1] < 4:
                counter -= 0.5
                if box[0] == 4 and box[1] == 8:
                    counter -= 1
        return int(self.Measure["box_on_the_way"]) * counter
