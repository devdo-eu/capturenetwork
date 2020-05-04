
from collections import defaultdict
from collections import deque
import logging
import threading
import time
import bot
import rules
import json
import copy
from battleground import Battleground
from namesaker import Namesaker


def tree(): return defaultdict(tree)


class Dispatcher(threading.Thread):
    def __init__(self, threadID, name, server):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.server = server
        self.games = 0
        self.bot_id = 0
        self.heartbeat = 0
        self.bots = deque()
        self.threads = []

    def loadData(self):
        try:
            with open('./history/game_list.json', 'r') as file:
                data = ''
                for line in file:
                    data += line
                if data != '':
                    data = json.loads(data)
                    for last_game in data['GAMES']:
                        pass
                    self.games = last_game['GAME_ID'] + 1
                    logging.info(self.name + f': game_list.json loaded.'
                                             f' GAME_ID set to {self.games}')
                else:
                    logging.info('game_list.json file is empty, GAME_ID set to 0.')
        except FileNotFoundError:
            logging.info(self.name + ': No game_list.json file, GAME_ID set to 0.')

    def createBattle(self, id, server):
        name = f'Battleground #{str(id)}'
        bot_1, bot_2 = self.bots.popleft(), self.bots.popleft()
        thread = Battleground(id, name, server, bot_1, bot_2)
        thread.start()
        return thread

    def saveRules(self):
        with open('./history/rules.json', 'w') as file:
            data = tree()
            data['RULES']['ROUND_TIME_MS'] = rules.timeOfRound
            data['RULES']['ROUNDS'] = rules.numberOfRounds
            file.writelines(json.dumps(data, sort_keys=True, indent=4))
        logging.info(self.name + ': Rules saved.')

    def sendGo(self, force=False):
        if self.heartbeat > 1500 or force:
            self.heartbeat = 0
            for bot_ in copy.copy(self.bots):
                try:
                    bot_.sendMessage('GO')
                except ConnectionResetError:
                    self.bots.remove(bot_)
                    self.bot_id -= 1
                except ConnectionAbortedError:
                    self.bots.remove(bot_)
                    self.bot_id -= 1
                except OSError:
                    self.bots.remove(bot_)
                    self.bot_id -= 1
        else:
            self.heartbeat += 1

    def run(self):
        logging.info(self.name + ': Loads GAME_ID...')
        self.loadData()
        logging.info(self.name + ': Writes rules.json...')
        self.saveRules()
        logging.info(self.name + ': Ready.')
        while self.server.closed is False:
            try:
                self.logBots()
                self.sendGo()

                if len(self.bots) >= 2:
                    self.sendGo(True)

                if len(self.bots) >= 2:
                    logging.info('Game can be played.....')
                    self.threads.append(self.createBattle(self.games, self.server))
                    self.games += 1
                    self.bot_id = 0
            except OSError as e:
                logging.info(f'OSError Exception: {e.strerror}')
        for t in self.threads:
            t.join()

    def logBots(self):
        data = self.server.get_data()
        cData = copy.copy(data)
        for peer_address, message in cData.items():
            if message == 'takeover':
                for conn in copy.copy(self.server.conns):
                    try:
                        conn.getpeername()
                    except OSError:
                        self.server.close_connection(conn)
                        self.server.conns.remove(conn)
                    if conn.getpeername() == peer_address and self.bot_id < 2:
                        self.server.conns.remove(conn)
                        del data[peer_address]
                        new_bot = bot.Bot(conn, self.bot_id, 'BOT_' + str(self.bot_id))
                        self.bots.append(new_bot)
                        self.bot_id += 1
                        logging.info("Dispatcher: Bot Connected...")
                        self.threads.append(Namesaker(new_bot, self.server))
                        break
            else:
                for conn in self.server.conns:
                    if conn.getpeername() == peer_address:
                        self.server.send_to_conn(peer_address, 'Access denied')
                        self.server.close_connection(conn)
                        self.server.conns.remove(conn)
                        del data[peer_address]
        time.sleep(0.05)
