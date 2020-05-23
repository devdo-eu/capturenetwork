"""@package mind
Package contains Mind class used as a logic module for PlayBot class
"""
from random import randrange
from json import JSONDecodeError, loads


class Mind:
    """
    Class contains all the methods responsible for the logic
    that guides the bot's actions during the course of the game
    """
    def __init__(self, log_method):
        """
        Constructor of bot mind. Here you can initialize all variables
        which you need to store for proper logic.
        :param log_method: Methods to log data. It tis given by bot API
        """
        self.__log = log_method
        self.moves = ['NOP()', 'PATCH()', 'SCAN()', 'OVERLOAD()', 'OVERHEAR()', 'EXPLOIT()', 'INFECT()']
        self.my_name = f'Ex.Bot'
        self.my_move = ''
        self.__move_ok = False
        self.base = 10000
        self.bfr = 50
        self.weights = [0, self.base, self.base, self.base, self.base, self.base, self.base]
        self.factors = [0, self.bfr, self.bfr, self.bfr, self.bfr, self.bfr, self.bfr]
        self.move_played = [0, 0, 0, 0, 0, 0, 0]

    def name(self):
        """
        Method used to send name to battle server. Unique name of the bot allows
        it to be easily identified when viewing record from the game.
        :return string object with name of bot
        """
        self.__log(f'Logged in as: {self.my_name}.')
        return self.my_name

    def move(self):
        """
        Method used at PHASE 1. Responsible for selecting the next round's play / movement
        :return string object with move chosen by bot
        """
        move_point = randrange(1, sum(self.weights))
        index = 0
        for w in self.weights:
            move_point -= w
            if move_point <= 0:
                break
            index += 1
        self.my_move = self.moves[index]
        return self.my_move

    def move_ack(self, data):
        """
        Method used at PHASE 2. Responsible for checking if battle server
        receive correctly move chosen by bot in PHASE 1.
        :param data: string object which contains move that the server assigns to this bot
        :return empty string if everything is ok / string with move if bot want to change his move
        """
        if self.__move_ok:
            return ''

        if self.my_move in data:
            self.__log('Move ACK.')
            self.__move_ok = True
            return ''
        else:
            return self.my_move

    def process_round(self, my_move, rival_move, round_won):
        index = self.moves.index(my_move)
        rival_index = self.moves.index(rival_move)
        self.move_played[index] += 1
        self.factors[index] += 1

        if round_won:
            self.weights[index] += int(self.base / self.factors[index])
            self.weights[rival_index] -= int(self.base / self.factors[index])
        else:
            self.weights[index] -= int(self.base / self.factors[index])
            self.weights[rival_index] += int(self.base / self.factors[index])

        if self.weights[index] <= 0:
            self.weights[index] = int(self.base / self.factors[index])

        if self.weights[rival_index] <= 0:
            self.weights[rival_index] = int(self.base / self.factors[index])

    def round_ends(self, data):
        """
        Method used at PHASE 3. Responsible for gathering information about flow of the game
        :param data: JSON object contains round summary.
        """
        try:
            self.__move_ok = False
            data = loads(data)
            rival_move = data['bot_2']['used']
            self.process_round(self.my_move, rival_move, data['winner'] == 1)
            self.__log(self.my_name + ": " + str(data['bot_1']['points']))
            self.__log('<< ' + str(rival_move))
            self.__log(str(data['bot_2']['name']) + ": " + str(data['bot_2']['points']) + "\r\n")
        except JSONDecodeError as e:
            self.__log(f'Exception: {e.msg} while parsing data.')

    def game_ends(self, data):
        """
        Method used after Skirmish. Responsible for saving important data after game ends.
        :param data: JSON object contains short game summary
        """
        self.__log(data)
        calculated = "\nweights:\n"
        played = "moves played:\n"

        for w in self.weights:
            calculated += str(w) + ' '

        for p in self.move_played:
            played += str(p) + ' '

        self.__log(calculated + "\r\n" + played)
