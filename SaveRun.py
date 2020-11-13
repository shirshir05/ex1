import csv
import pathlib
from configparser import ConfigParser
from datetime import datetime
import random


class SaveRun:
    # todo need add to csv
    "Experiment seed	Individual's Generation	Individual ID	Solution length	# boxes in place"

    def __init__(self):
        today = datetime.now()
        dt_string = today.strftime("%d-%m-%Y %H-%M")
        self.path = str(pathlib.Path().absolute()) + "/Experiments/" + str(dt_string) + ".csv"
        self.file = open(self.path, "w")

    def write_config(self, name):
        config_object = ConfigParser()
        config_object.read(name)
        dict_config = [{section: dict(config_object[section]) for section in config_object.sections()}]
        with open(self.path, 'w', newline='') as myfile:
            writer_list = csv.writer(myfile, delimiter=',')
            list_key = []
            list_value = []
            for data in dict_config:
                for section in data:
                    for i, j in data[section].items():
                        list_key.append(i)
                        list_value.append(j)
            writer_list.writerow(list_key)
            writer_list.writerow(list_value)

            writer_header = csv.writer(myfile, delimiter=',')
            writer_header.writerow(['epoch', 'min', 'sum', 'average'])

    @staticmethod
    def write_permutations():
        """
            write permutations to file
            because It takes a long time to produce a permutation - run i  server
        """
        def string_split(string):
            list_move = []
            for i in string:
                if i == " ":
                    continue
                list_move.append(i)
            return list_move
        opt_solution = "ullluuuLUllDlldddrRRRRRRRRRRRRurDllllllllllllllulldRRRRRRRRRRRRRdrUluRRlldlllllluuululldDDuulldddrRRRRRRRRRRRRlllllllluuulLulDDDuulldddrRRRRRRRRRRRurDlllllllluuululuurDDllddddrrruuuLLulDDDuulldddrRRRRRRRRRRdrUluRldlllllluuuluuullDDDDDuulldddrRRRRRRRRRRR"
        size_feature = 500
        size_population_init = 1000
        data_set_permutation = []
        for i in range(size_population_init):
            permutation = random.sample(opt_solution, abs(size_feature - len(opt_solution)))
            permutation = permutation + list(opt_solution)
            permutation = ''.join(random.sample(permutation, size_feature))
            data_set_permutation.append(string_split(permutation))
        with open(str(pathlib.Path().absolute()) + "/File/permutations.csv", 'w') as file:
            wr = csv.writer(file, quoting=csv.QUOTE_ALL)
            for i in data_set_permutation:
                wr.writerow(i)

    @staticmethod
    def read_permutations():
        """
            return list of all permutations
        """
        with open(str(pathlib.Path().absolute()) + "/File/permutations.csv", newline='') as file:
            reader = csv.reader(file)
            data = list(reader)
            data = [ele for ele in data if ele != []]
            return data

    def write_epoch(self, epoch, min_fitness, sum, number_pop):
        with open(self.path, 'a', newline='') as myfile:
            writer = csv.writer(myfile, delimiter=',')
            writer.writerow([epoch, min_fitness, sum, sum/number_pop])


if __name__ == '__main__':
    run = SaveRun()
    run.write_permutations()
    # run.read_permutations()
    # run.write_config()
