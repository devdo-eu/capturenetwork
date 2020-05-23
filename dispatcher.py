import copy
import json
import logging
import threading
import time
from collections import defaultdict
from collections import deque

import bot
import rules
from battleground import Battleground
from enumeration import GamesListFileField as gff
from enumeration import RulesFileField as rff
from namesaker import NameSaker


def tree(): return defaultdict(tree)


class Dispatcher(threading.Thread):
    """
    Class responsible for logging bots and creating battles for them
    Object of this class will split / dispatch logged in bots to battles with each other
    """
    def __init__(self, thread_id, name, server):
        threading.Thread.__init__(self)
        self.__thread_id = thread_id
        self.__name = name
        self.__server = server
        self.__games = 0
        self.__bot_id = 0
        self.__heartbeat = 0
        self.__bots = deque()
        self.__threads = []

    def __getLastGameID(self):
        """
        Method responsible for loading game_list.json file and obtaining last game id
        """
        try:
            with open('./history/game_list.json', 'r') as file:
                data = ''
                for line in file:
                    data += line

                if data != '':
                    data = json.loads(data)
                    max_game_id = 0
                    for game in data:
                        current_game_id = game[gff.GAME_ID.value]
                        max_game_id = current_game_id if current_game_id > max_game_id else max_game_id

                    self.__games = max_game_id + 1
                    logging.info(self.__name + f': game_list.json loaded.'
                                               f' GAME_ID set to {self.__games}')

                else:
                    logging.info('game_list.json file is empty, GAME_ID set to 0.')
        except FileNotFoundError:
            logging.info(self.__name + ': No game_list.json file, GAME_ID set to 0.')

    def __createBattle(self, id, server):
        """
        Method used to create Battleground object
        which will handle all bot battle operations
        :param id: order number of Battleground
        :param server: TCP/IP server object for handling communication with bots
        :return: Thread object with Battleground ready for battle
        """
        name = f'Battleground #{str(id)}'
        bot_1, bot_2 = self.__bots.popleft(), self.__bots.popleft()
        thread = Battleground(id, name, server, bot_1, bot_2)
        thread.start()
        return thread

    def __saveRules(self):
        """
        Helper method used to save server rules to file rules.json
        """
        with open('./history/rules.json', 'w') as file:
            data = tree()
            data[rff.RULES.value][rff.ROUND_TIME_MS.value] = rules.timeOfRound
            data[rff.RULES.value][rff.ROUNDS.value] = rules.numberOfRounds
            file.writelines(json.dumps(data, sort_keys=True, indent=4))

        logging.info(self.__name + ': Rules saved.')

    def __sendGo(self, force=False):
        """
        Helper method used to check if bots are still connected
        when Dispatcher is creating Battleground object.
        It simply sends messages to check if channel is open.
        :param force: Flag used to force checking
        """
        if self.__heartbeat > 1500 or force:
            self.__heartbeat = 0
            for bot_ in copy.copy(self.__bots):
                try:
                    bot_.sendMessage('GO')
                    bot_.sendMessage('GO')
                except (ConnectionResetError, ConnectionAbortedError, OSError):
                    self.__bots.remove(bot_)
                    self.__bot_id -= 1

        else:
            self.__heartbeat += 1

    def __logBots(self):
        """
        Method responsible for login bots.
        It is checking password for connected clients and ask bot for its name.
        """
        data = self.__server.getData()
        data_copy = copy.copy(data)
        for peer_address, message in data_copy.items():
            if message == 'takeover':
                for connection_copy in copy.copy(self.__server.conns):
                    try:
                        connection_copy.getpeername()
                    except OSError:
                        self.__server.closeConnection(connection_copy)
                        self.__server.conns.remove(connection_copy)

                    if connection_copy.getpeername() == peer_address and self.__bot_id < 2:
                        self.__server.conns.remove(connection_copy)
                        del data[peer_address]
                        new_bot = bot.Bot(connection_copy, self.__bot_id, 'BOT_' + str(self.__bot_id))
                        self.__bots.append(new_bot)
                        self.__bot_id += 1
                        logging.info("Dispatcher: Bot Connected...")
                        name_seeker = NameSaker(new_bot, self.__server)
                        name_seeker.start()
                        self.__threads.append(name_seeker)
                        break

            else:
                for connection_copy in self.__server.conns:
                    if connection_copy.getpeername() == peer_address:
                        self.__server.sendToConn(peer_address, 'Access denied')
                        self.__server.closeConnection(connection_copy)
                        self.__server.conns.remove(connection_copy)
                        del data[peer_address]

        time.sleep(0.05)

    def run(self):
        """
        Main method of Dispatcher class. Responsible for handling all of its logic
        """
        logging.info(self.__name + ': Loads GAME_ID...')
        self.__getLastGameID()
        logging.info(self.__name + ': Writes rules.json...')
        self.__saveRules()
        logging.info(self.__name + ': Ready.')
        while self.__server.closed is False:
            try:
                self.__logBots()
                self.__sendGo()

                if len(self.__bots) >= 2:
                    self.__sendGo(True)
                    time.sleep(1)

                if len(self.__bots) >= 2:
                    logging.info('Game can be played.....')
                    self.__threads.append(self.__createBattle(self.__games, self.__server))
                    self.__games += 1
                    self.__bot_id = 0

            except OSError as e:
                logging.info(f'OSError Exception: {e.strerror}')
        for t in self.__threads:
            t.join()
