"""@package mind
Package contains Mind class used as a logic module for PlayBot class
"""
from random import randrange
from json import JSONDecodeError, loads


class Mind:
    def __init__(self, log_method, send_method):
        self.__log = log_method
        self.__send = send_method
        self.__my_name = f'ExampleBot_{randrange(500)}'
        self.__moves = ['NOP()', 'PATCH()', 'SCAN()', 'OVERLOAD()', 'OVERHEAR()', 'EXPLOIT()', 'INFECT()']
        self.__my_move = ''
        self.__move_ok = False

    def name(self):
        self.__send(self.__my_name)
        self.__log(f'Logged in as: {self.__my_name}.')

    def move(self):
        self.__my_move = self.__moves[randrange(1, len(self.__moves))]
        self.__send(self.__my_move)

    def move_ack(self, data):
        if self.__move_ok:
            return

        if self.__my_move in data:
            self.__log('Move ACK.')
            self.__move_ok = True
        else:
            self.__send(self.__my_move)

    def round_ends(self, data):
        try:
            self.__move_ok = False
            data = loads(data)
            self.__log(data['BOT_1'])
        except JSONDecodeError as e:
            self.__log(f'Exception: {e.msg} while parsing data.')

    def game_ends(self, data):
        self.__log(data)
