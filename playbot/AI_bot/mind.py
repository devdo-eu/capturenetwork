"""@package mind
Package contains Mind class used as a logic module for PlayBot class
"""
from json import JSONDecodeError, loads
from keras.models import model_from_json
from keras.optimizers import Adam
from collections import deque
import numpy as np


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
        :param agent: Name of agent files to load
        """
        self.__log = log_method
        self.__moves = ['NOP()', 'PATCH()', 'SCAN()', 'OVERLOAD()', 'OVERHEAR()', 'EXPLOIT()', 'INFECT()']
        self.__my_name = f'AI Network'
        self.__my_move = ''
        self.__move_ok = False
        self.model = []
        self.state = [0] * 108
        self.last_all_bot0 = deque()
        self.last_all_bot1 = deque()
        self.load_agent('network')

    def load_agent(self, agent):
        json_file = open(f'{agent}.json', 'r')
        loaded_model_json = json_file.read()
        json_file.close()
        self.model = model_from_json(loaded_model_json)
        # load weights into new model
        self.model.load_weights(f'{agent}.h5')
        self.model.compile(loss='mse', optimizer=Adam(lr=10e-5))
        print("Loaded and compiled model from disk")
        print(self.model.summary())

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
        self.state = np.reshape(self.state, (1, 108))
        self.__my_move = np.argmax(self.model.predict(self.state)[0])
        self.__my_move = self.__moves[self.__my_move]
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
            self.__move_ok = True
            return ''
        else:
            return self.__my_move

    def define_state(self, msg):

        state0, state1 = self.process_last(msg['bot_1']['used'], msg['bot_2']['used'])
        state0 = list(np.array(state0).reshape(-1))
        state1 = list(np.array(state1).reshape(-1))
        rival_move = self.__moves.index(msg['bot_2']['used'])
        my_move = self.__moves.index(msg['bot_1']['used'])
        rp = msg["bot_2"]["points"]
        mp = msg["bot_1"]["points"]
        self.__log(f'\nMy points:\t{mp}\nRival:\t\t{rp}\nAdvantage:\t{mp - rp}')

        self.state = [msg['winner'] / 3.0, msg['advantage'] / 3.0, rival_move / 6.0, my_move / 6.0]
        self.state = self.state + state0 + state1
        return self.state

    def round_ends(self, data):
        """
        Method used at PHASE 3. Responsible for gathering information about flow of the game
        :param data: JSON object contains round summary.
        """
        try:
            self.__move_ok = False
            data = loads(data)
            self.define_state(data)
        except JSONDecodeError as e:
            self.__log(f'Exception: {e.msg} while parsing data.')

    def game_ends(self, data):
        """
        Method used after Skirmish. Responsible for saving important data after game ends.
        :param data: JSON object contains short game summary
        """
        self.__log(data)

    def process_last(self, bot0_method, bot1_method):

        self.last_all_bot0.append(self.__moves.index(bot0_method))
        self.last_all_bot1.append(self.__moves.index(bot1_method))

        last_bot0 = self.last_all_bot0
        last_bot1 = self.last_all_bot1

        mem_bot0 = [self.get_move(last_bot0, 2), self.get_move(last_bot0, 3),
                    self.get_move(last_bot0, 4), self.get_move(last_bot0, 5),
                    self.get_move(last_bot0, 6), self.get_move(last_bot0, 7),
                    self.get_move(last_bot0, 8), self.get_move(last_bot0, 9),
                    self.get_move(last_bot0, 10), self.get_move(last_bot0, 11)] + \
                    self.recalculate(last_bot0, 0, 20) + self.recalculate(last_bot0, 20, 20) + \
                    self.recalculate(last_bot0, 40, 20) + self.recalculate(last_bot0, 60, 20) + \
                    self.recalculate(last_bot0, 80, 20) + self.recalculate(last_bot0, 100, 20)

        mem_bot1 = [self.get_move(last_bot1, 2), self.get_move(last_bot1, 3),
                    self.get_move(last_bot1, 4), self.get_move(last_bot1, 5),
                    self.get_move(last_bot1, 6), self.get_move(last_bot1, 7),
                    self.get_move(last_bot1, 8), self.get_move(last_bot1, 9),
                    self.get_move(last_bot1, 10), self.get_move(last_bot1, 11)] + \
                    self.recalculate(last_bot1, 0, 20) + self.recalculate(last_bot1, 20, 20) + \
                    self.recalculate(last_bot1, 40, 20) + self.recalculate(last_bot1, 60, 20) + \
                    self.recalculate(last_bot1, 80, 20) + self.recalculate(last_bot1, 100, 20)
        return mem_bot0, mem_bot1

    @staticmethod
    def get_move(last_moves, index):
        move = 0

        if len(last_moves) < index:
            return move

        return last_moves[len(last_moves) - index - 1] / 6.0

    @staticmethod
    def recalculate(last_moves, start, length):
        stats = [0, 0, 0, 0, 0, 0, 0]
        if len(last_moves) < start:
            return stats

        if len(last_moves) < length + start:
            length = len(last_moves) - start

        if length == 0:
            return stats

        for i in range(len(last_moves) - start - 1, len(last_moves) - start - length - 1, -1):
            stats[last_moves[i]] += 1

        for i in range(len(stats)):
            stats[i] = stats[i] / length

        return stats
