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
        self.__moves = ['NOP()', 'PATCH()', 'SCAN()', 'OVERLOAD()', 'OVERHEAR()', 'EXPLOIT()', 'INFECT()']
        self.__my_name = f'ExampleBot_{randrange(500)}'
        self.__my_move = ''
        self.__move_ok = False

    def name(self):
        """
        Method used to send name to battle server. Unique name of the bot allows
        it to be easily identified when viewing record from the game.
        :return string object with name of bot
        """
        self.__log(f'Logged in as: {self.__my_name}.')
        return self.__my_name

    def move(self):
        """
        Method used at PHASE 1. Responsible for selecting the next round's play / movement
        :return string object with move chosen by bot
        """
        self.__my_move = self.__moves[randrange(1, len(self.__moves))]
        return self.__my_move

    def move_ack(self, data):
        """
        Method used at PHASE 2. Responsible for checking if battle server
        receive correctly move chosen by bot in PHASE 1.
        :param data: string object which contains move that the server assigns to this bot
        :return empty string if everything is ok / string with move if bot want to change his move
        """
        if self.__move_ok:
            return ''

        if self.__my_move in data:
            self.__log('Move ACK.')
            self.__move_ok = True
            return ''
        else:
            return self.__my_move

    def round_ends(self, data):
        """
        Method used at PHASE 3. Responsible for gathering information about flow of the game
        :param data: JSON object contains round summary.
        """
        try:
            self.__move_ok = False
            data = loads(data)
            self.__log(data['BOT_1'])
        except JSONDecodeError as e:
            self.__log(f'Exception: {e.msg} while parsing data.')

    def game_ends(self, data):
        """
        Method used after Skirmish. Responsible for saving important data after game ends.
        :param data: JSON object contains short game summary
        """
        self.__log(data)
