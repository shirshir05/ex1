import pathlib
from queue import Queue

NUMBER_COL = 19


class Game:

    @staticmethod
    def is_valid_value(char):
        if (char == ' ' or  # floor
                char == '#' or  # wall
                char == '@' or  # worker on floor
                char == '.' or  # dock
                char == '*' or  # box on dock
                char == '$' or  # box
                char == '+'):  # worker on dock
            return True
        else:
            return False

    def __init__(self, name_file, number_level):
        self.queue = Queue()
        self.matrix = [[] for i in range(0, number_level)]
        file = open(str(pathlib.Path().absolute()) + '/File/' + name_file, 'r')
        level = 0
        level_found = False
        for line in file:
            if level_found:
                level_found = False
                continue
            elif line.find(";") == -1:
                row = []
                index_col = 0
                for c in line:
                    if index_col == NUMBER_COL:
                        continue
                    if c != '\n' and self.is_valid_value(c):
                        row.append(c)
                        index_col += 1
                    elif c == '\n':
                        for i in range(index_col, NUMBER_COL):
                            row.append("")
                    else:
                        print("error input")

                self.matrix[level].append(row)
            else:
                level += 1
                level_found = True

    def print_board(self):
        for i in range(0, len(self.matrix)):
            print("level ", i + 1)
            for j in range(0, len((self.matrix[i]))):
                print(self.matrix[i][j])
            print("")

    def write_board(self, name, epoch, worker_in_deadlock, count_left_box, euclidean_distance):
        list_board = [[i for i in range(0, len(self.matrix))]]
        for i in range(0, len(self.matrix)):
            for j in range(0, len((self.matrix[i]))):
                list_board[i].append(self.matrix[i][j])
        with open(str(name) + '.txt', 'a') as filehandle:
            filehandle.write("epoch = %d,  " %epoch)
            filehandle.write("worker_in_deadlock = %d,  " %worker_in_deadlock)
            filehandle.write("euclidean_distance = %d " %euclidean_distance)
            filehandle.write("count_left_box = %d " %count_left_box)
            for listitem in list_board:
                for item in listitem:
                    filehandle.write('%s\n' % item)


    def get_matrix(self):
        return self.matrix

    def get_content(self, level, row, col):
        return self.matrix[level - 1][row][col]

    def set_content(self, level, row, col, content):
        if self.is_valid_value(content):
            self.matrix[level - 1][row][col] = content
        else:
            print("ERROR: Value '" + content + "' to be added is not valid")

    def worker(self, level):
        """"
        position of worker
        :return:
                 x - row number
                 y - col number
                 pos - @ or +
        """
        col_index = 0
        row_index = 0
        for row in self.matrix[level - 1]:
            for pos in row:
                if pos == '@' or pos == '+':
                    return row_index, col_index, pos
                else:
                    col_index = col_index + 1
            row_index = row_index + 1
            col_index = 0

    def can_move(self, level, row, col):
        return self.get_content(level, self.worker(level)[0] + row, self.worker(level)[1] + col) not in ['#', '*', '$']

    def next(self, level, row, col):
        return self.get_content(level, self.worker(level)[0] + row, self.worker(level)[1] + col)

    def can_push(self, level, row, col):
        return self.next(level, row, col) in ['*', '$'] and self.next(level, row + row, col + col) in [' ', '.']

    def is_completed(self, level):
        for row in self.matrix[level - 1]:
            for cell in row:
                if cell == '$':
                    return False
        return True

    def move_box(self, level, x, y, a, b):
        #        (x,y) -> move to do
        #        (a,b) -> box to move
        current_box = self.get_content(level, x, y)
        future_box = self.get_content(level, x + a, y + b)
        if current_box == '$' and future_box == ' ':
            self.set_content(level, x + a, y + b, '$')
            self.set_content(level, x, y, ' ')
        elif current_box == '$' and future_box == '.':
            self.set_content(level, x + a, y + b, '*')
            self.set_content(level, x, y, ' ')
        elif current_box == '*' and future_box == ' ':
            self.set_content(level, x + a, y + b, '$')
            self.set_content(level, x, y, '.')
        elif current_box == '*' and future_box == '.':
            self.set_content(level, x + a, y + b, '*')
            self.set_content(level, x, y, '.')

    def move(self, level, x, y, save):
        if self.can_move(level, x, y):
            current = self.worker(level)
            future = self.next(level, x, y)
            if current[2] == '@' and future == ' ':
                self.set_content(level, current[0] + x, current[1] + y, '@')
                self.set_content(level, current[0], current[1], ' ')
                if save: self.queue.put((x, y, False))
            elif current[2] == '@' and future == '.':
                self.set_content(level, current[0] + x, current[1] + y, '+')
                self.set_content(level, current[0], current[1], ' ')
                if save: self.queue.put((x, y, False))
            elif current[2] == '+' and future == ' ':
                self.set_content(level, current[0] + x, current[1] + y, '@')
                self.set_content(level, current[0], current[1], '.')
                if save: self.queue.put((x, y, False))
            elif current[2] == '+' and future == '.':
                self.set_content(level, current[0] + x, current[1] + y, '+')
                self.set_content(level, current[0], current[1], '.')
                if save: self.queue.put((x, y, False))
        elif self.can_push(level, x, y):
            current = self.worker(level)
            future = self.next(level, x, y)
            future_box = self.next(level, x + x, y + y)
            if current[2] == '@' and future == '$' and future_box == ' ':
                self.move_box(level, current[0] + x, current[1] + y, x, y)
                self.set_content(level, current[0], current[1], ' ')
                self.set_content(level, current[0] + x, current[1] + y, '@')
                if save: self.queue.put((x, y, True))
            elif current[2] == '@' and future == '$' and future_box == '.':
                self.move_box(level, current[0] + x, current[1] + y, x, y)
                self.set_content(level, current[0], current[1], ' ')
                self.set_content(level, current[0] + x, current[1] + y, '@')
                if save: self.queue.put((x, y, True))
            elif current[2] == '@' and future == '*' and future_box == ' ':
                self.move_box(level, current[0] + x, current[1] + y, x, y)
                self.set_content(level, current[0], current[1], ' ')
                self.set_content(level, current[0] + x, current[1] + y, '+')
                if save: self.queue.put((x, y, True))
            elif current[2] == '@' and future == '*' and future_box == '.':
                self.move_box(level, current[0] + x, current[1] + y, x, y)
                self.set_content(level, current[0], current[1], ' ')
                self.set_content(level, current[0] + x, current[1] + y, '+')
                if save: self.queue.put((x, y, True))
            if current[2] == '+' and future == '$' and future_box == ' ':
                self.move_box(level, current[0] + x, current[1] + y, x, y)
                self.set_content(level, current[0], current[1], '.')
                self.set_content(level, current[0] + x, current[1] + y, '@')
                if save: self.queue.put((x, y, True))
            elif current[2] == '+' and future == '$' and future_box == '.':
                self.move_box(level, current[0] + x, current[1] + y, x, y)
                self.set_content(level, current[0], current[1], '.')
                self.set_content(level, current[0] + x, current[1] + y, '+')
                if save: self.queue.put((x, y, True))
            elif current[2] == '+' and future == '*' and future_box == ' ':
                self.move_box(level, current[0] + x, current[1] + y, x, y)
                self.set_content(level, current[0], current[1], '.')
                self.set_content(level, current[0] + x, current[1] + y, '+')
                if save: self.queue.put((x, y, True))
            elif current[2] == '+' and future == '*' and future_box == '.':
                self.move_box(level, current[0] + x, current[1] + y, x, y)
                self.set_content(level, current[0], current[1], '.')
                self.set_content(level, current[0] + x, current[1] + y, '+')
                if save: self.queue.put((x, y, True))
        else:
            # can't move
            return False
        return True

    def play(self, level, list_move):
        #print("start")
        index = 0
        for move in list_move:
            if self.is_completed(level):
                return True
            if move == 'L' or move == 'l':
                self.move(level, 0, -1, True)
            elif move == 'R' or move == 'r':
                self.move(level, 0, 1, True)
            elif move == 'U' or move == 'u':
                self.move(level, -1, 0, True)
            elif move == 'D' or move == 'd':
                self.move(level, 1, 0, True)
            index += 1
        self.print_board()
        return self.is_completed(level)  # True/ False

    @staticmethod
    def string_split():
        string = "ullluuuLUllDlldddrRRRRRRRRRRRRurDllllllllllllllulldRRRRRRRRRRRRRdrUluRRlldlllllluuululldDDuulldddrRRRRRRRRRRRRlllllllluuulLulDDDuulldddrRRRRRRRRRRRurDlllllllluuululuurDDllddddrrruuuLLulDDDuulldddrRRRRRRRRRRdrUluRldlllllluuuluuullDDDDDuulldddrRRRRRRRRRRR"
        list_move = []
        for i in string:
            if i == " ":
                continue
            list_move.append(i)
        return list_move


if __name__ == '__main__':
    game = Game("one_input.txt", 1)
    # game.print_board()
    print(game.play(1, Game.string_split()))

