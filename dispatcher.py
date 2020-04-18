
from collections import defaultdict
import logging
import threading
import time
import bot
import rules
import json
import copy
from battleground import Battleground


def tree(): return defaultdict(tree)


class Dispatcher(threading.Thread):
    def __init__(self, threadID, name, server):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.server = server
        self.games = 0
        self.bot_id = 0
        self.bots = []
        self.threads = []

    def loadData(self):
        try:
            with open('game_list.json', 'r') as file:
                for last_line in file:
                    pass
                data = last_line
                if data != '':
                    data = json.loads(data)
                    self.games = data['GAME_ID'] + 1
                    logging.info(self.name + f': game_list.json loaded.'
                                             f' GAME_ID set to {self.games}')
        except FileNotFoundError as e:
            logging.info(self.name + ": No game_list.json file, GAME_ID set to 0.")

    def createBattle(self, id, server):
        name = f'Battleground #{str(id)}'
        bot_1, bot_2 = self.bots.pop(), self.bots.pop()
        thread = Battleground(id, name, server, bot_1, bot_2)
        thread.start()
        return thread

    def saveRules(self):
        with open('rules.json', 'w') as file:
            data = tree()
            data['ROUND_TIME_MS'] = rules.timeOfRound
            data['ROUNDS'] = rules.numberOfRounds
            file.writelines(json.dumps(data))
        logging.info(self.name + ": Rules saved.")

    def sendGo(self):
        for bot in self.bots:
            try:
                bot.sendMessage("GO\r\n")
            except ConnectionResetError as e:
                self.bots.remove(bot)
                self.bot_id -= 1
            except ConnectionAbortedError as e:
                self.bots.remove(bot)
                self.bot_id -= 1
            except OSError as e:
                self.bots.remove(bot)
                self.bot_id -= 1

    def run(self):
        logging.info(self.name + ": Loads GAME_ID...")
        self.loadData()
        logging.info(self.name + ": Writes rules.json...")
        self.saveRules()
        logging.info(self.name + ": Ready.")
        while self.server.closed is False:
            try:
                self.logBots()
                if len(self.bots) > 0:
                    self.sendGo()

                if len(self.bots) >= 2:
                    logging.info("Game can be played.....")
                    self.threads.append(self.createBattle(self.games, self.server))
                    self.games += 1
                    self.bot_id = 0
            except OSError as e:
                logging.info(f"OSError Exception: {e.strerror}")
        for t in self.threads:
            t.join()

    def logBotNames(self):
        time.sleep(0.5)
        data = self.server.get_data()
        cData = copy.copy(data)
        for k, v in cData.items():
            for bot in self.bots:
                try:
                    if bot.connection().getpeername() == k and 'BOT_' in bot.name():
                        bot.putName(v[:-2])
                        del data[k]
                except OSError as e:
                    self.bots.remove(bot)
                    self.bot_id -= 1

    def logBots(self):
        data = self.server.get_data()
        cData = copy.copy(data)
        for k, v in cData.items():
            if v[:-2] == 'takeover':
                for conn in copy.copy(self.server.conns):
                    try:
                        temp = conn.getpeername()
                    except OSError:
                        self.server.close_connection(conn)
                        self.server.conns.remove(conn)
                    if conn.getpeername() == k and self.bot_id < 2:
                        self.server.conns.remove(conn)
                        del data[k]
                        new_bot = bot.Bot(conn, self.bot_id, 'BOT_' + str(self.bot_id))
                        self.bots.append(new_bot)
                        self.bot_id += 1
                        logging.info("Dispatcher: Bot Connected...")
                        self.logBotNames()
                        break
            else:
                for conn in self.server.conns:
                    if conn.getpeername() == k:
                        self.server.send_to_conn(k, 'Access denied\r\n')
                        self.server.close_connection(conn)
                        self.server.conns.remove(conn)
                        del data[k]
        time.sleep(0.1)