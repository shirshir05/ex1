import csv
import itertools
import pathlib
from configparser import ConfigParser
from datetime import date, datetime


class SaveRun:
    # todo need add to csv
    "Experiment seed	Individual's Generation	Individual ID	Solution length	# boxes in place"

    def __init__(self):
        today = datetime.now()
        dt_string = today.strftime("%d-%m-%Y %H-%M")
        self.path = str(pathlib.Path().absolute()) + "/Experiments/" + str(dt_string) + ".csv"
        self.file = open(self.path, "w")

    def write_config(self):
        config_object = ConfigParser()
        config_object.read("config.ini")
        dict_config = [{section: dict(config_object[section]) for section in config_object.sections()}]
        with open(self.path, 'w', newline='') as myfile:
            writer_list = csv.writer(myfile, delimiter=',')
            for data in dict_config:
                for section in data:
                    writer_list.writerow([section])
                    writer_list.writerow(list(data[section].items()))
            writer_header = csv.writer(myfile, delimiter=',')
            writer_header.writerow(['epoch', 'max', 'sum', 'average'])

    @staticmethod
    def write_permutations():
        """
            write permutations to file
            because It takes a long time to produce a permutation - run i  server
        """
        def string_split():
            # string = "ullluuuLUllDlldddrRRRRRRRRRRRRurDllllllllllllllulldRRRRRRRRRRRRRdrUluRRlldlllllluuululldDDuulldddrRR RRRRRRRRRRlllllllluuulLulDDDuulldddrRRRRRRRRRRRurDlllllllluuululuurDDllddddrrruuuLLulDDDuulldddrRRRRRRRRRRdrUluRldlllllluuuluuullDDDDDuulldddrRRRRRRRRRRR"
            string = "ulldddrRR"
            list_move = []
            for i in string:
                if i == " ":
                    continue
                list_move.append(i)
            return list_move

        list_solution = string_split()
        # todo change permutations
        data_set_permutation = list(itertools.permutations(list_solution))
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

    def write_epoch(self, epoch, max, sum, number_pop):
        with open(self.path, 'a', newline='') as myfile:
            writer = csv.writer(myfile, delimiter=',')
            writer.writerow([epoch, max, sum, sum/number_pop])
            myfile


if __name__ == '__main__':
    run = SaveRun()
    # run.write_permutations()
    # run.read_permutations()
    run.write_config()
