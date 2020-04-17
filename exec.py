# -*- coding: utf-8 -*-
"""
Created on Thu Nov 21 19:32:07 2019

@author: Grzesiek-UC
"""
from TCP_Server import SelectorServer
from collections import defaultdict
import logging
import threading
import time
import bot
import rules
import json
import copy
from datetime import datetime


def tree(): return defaultdict(tree)


def cBattleThread(iden, server, bot_1, bot_2):
    thread = myThread(iden, "Battle Thread #" + str(iden), server, bot_1, bot_2)
    thread.start()
    return thread


class botDispachThread(threading.Thread):
    def __init__(self, threadID, name, server):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.server = server
        self.games = 0
        self.bot_id = 0
        self.bots = []
        self.threads = []

    def run(self):
        logging.info(self.name + " Ready.")
        while server.closed is False:
            try:
                self.logBots()
                if len(self.bots) >= 2:
                    self.logBots()
                    bot_1, bot_2 = self.bots.pop(), self.bots.pop()
                    logging.info("Game can be played.....")
                    self.threads.append(cBattleThread(self.games, server, bot_1, bot_2))
                    self.games += 1
                    self.bot_id = 0
            except OSError as e:
                logging.info(f"OSError Exception: {e.strerror}")
        for t in self.threads:
            t.join()


    def logBots(self):
        data = server.get_data()
        cData = copy.copy(data)
        for k, v in cData.items():
            if v[:-2] == 'takeover':
                for conn in copy.copy(server.conns):
                    try:
                        temp = conn.getpeername()
                    except OSError:
                        server.close_connection(conn)
                        server.conns.remove(conn)
                    if conn.getpeername() == k and self.bot_id < 2:
                        server.conns.remove(conn)
                        del data[k]
                        new_bot = bot.Bot(conn, self.bot_id, 'BOT_' + str(self.bot_id))
                        self.bots.append(new_bot)
                        self.bot_id += 1
                        logging.info("Dispatcher: Bot Connected...")
                        break
            else:
                for tbot in self.bots:
                    if tbot.connection().getpeername() == k:
                        tbot.putName(v[:-2])
                        del data[k]
                for conn in server.conns:
                    if conn.getpeername() == k:
                        server.send_to_conn(k, 'Access denied\r\n')
                        server.close_connection(conn)
                        server.conns.remove(conn)
                        del data[k]
        time.sleep(0.1)


class myThread(threading.Thread):
    def __init__(self, threadID, name, server, bot_1, bot_2):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.server = server
        self.bots = [bot_1, bot_2]
        self.timestamp = time.time()
        self.passedRounds = 0
        self.fileLogName = ''
        self.fileHandle = ''
        self.gameRecord = []
        self.gameHistory = []

    def runRound(self):
        self.timestamp = time.time()
        for tbot in self.bots:
            tbot.putMethod('NOP()', False)
            time.sleep(rules.timeOfRound / 3000)
            tbot.sendMessage('Command>\r\n')
        time.sleep(rules.timeOfRound * 2 / 3000)
        data = server.get_data()
        cData = copy.copy(data)
        for k, v in cData.items():
            for tbot in self.bots:
                if tbot.connection().getpeername() == k:
                    if v[:5] == 'NAME(' and v[-3:-2] == ')':
                        tbot.putName(v[5:-3])
                    else:
                        tbot.putMethod(v[:-2])
                    del data[k]
                    break
        self.passedRounds += 1

    def concludeTurn(self):
        if len(self.bots) != 2:
            return

        bot_1, bot_2 = self.bots[0], self.bots[1]
        winner = bot_1.name()
        result_1 = rules.methodToMethodResult[bot_1.method()][bot_2.method()]
        advantage_1 = rules.methodToMethodAdvantage[bot_1.method()][bot_2.method()]
        adv = str(bot_1.name())

        if result_1 is rules.Result.FASTER_WINNER:
            if bot_1.advantage() == bot_2.advantage():
                if bot_1.timestamp() < bot_2.timestamp():
                    bot_1.addPrize()
                else:
                    bot_2.addPrize()
                    winner = bot_2.name()
            elif bot_1.advantage():
                bot_1.addPrize()
            else:
                bot_2.addPrize()
                winner = bot_2.name()
        elif result_1 is rules.Result.WIN:
            bot_1.addPrize()
        elif result_1 is rules.Result.LOSE:
            bot_2.addPrize()
            winner = bot_2.name()
        else:
            winner = 'DRAW'

        if advantage_1 is rules.Advantage.GAIN:
            bot_1.putAdvantage(True)
            bot_2.putAdvantage(False)
        elif advantage_1 is rules.Advantage.LOST:
            bot_1.putAdvantage(False)
            bot_2.putAdvantage(True)
            adv = str(bot_2.name())
        else:
            bot_1.putAdvantage(False)
            bot_2.putAdvantage(False)
            adv = 'Time'

        summary = tree()
        summary['TIME'] = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        summary['WINNER'], summary['ADVANTAGE'] = winner, adv
        summary['ROUNDS'] = str(self.passedRounds) + '/' + str(rules.numberOfRounds)

        msg_1 = copy.copy(summary)
        msg_2 = copy.copy(summary)
        msg_1['BOT_1'], msg_1['BOT_2'] = bot_1.toJSON(self.timestamp), bot_2.toJSON(self.timestamp)
        msg_2['BOT_1'], msg_2['BOT_2'] = bot_2.toJSON(self.timestamp), bot_1.toJSON(self.timestamp)

        bot_1.sendMessage(json.dumps(msg_1) + '\r\n')
        bot_2.sendMessage(json.dumps(msg_2) + '\r\n')
        self.gameRecord.append(json.dumps(msg_1) + '\r\n')
        logging.info(json.dumps(summary))

    def concludeGame(self):
        if len(self.bots) != 2:
            return

        bot_1, bot_2 = self.bots[0], self.bots[1]
        results = tree()
        if bot_1.points() > bot_2.points():
            results['WINNER']['NAME'], results['WINNER']['POINTS'] = bot_1.name(), bot_1.points()
        elif bot_1.points() < bot_2.points():
            results['WINNER']['NAME'], results['WINNER']['POINTS'] = bot_2.name(), bot_2.points()
        else:
            results['WINNER']['NAME'], results['WINNER']['POINTS'] = 'DRAW - NO WINNER', 0

        bot_1.sendMessage(json.dumps(results))
        bot_2.sendMessage(json.dumps(results))
        self.gameRecord.append(json.dumps(results))
        self.gameHistory.append(self.gameRecord)
        self.fileHandle.writelines("%s" % item for item in self.gameRecord)
        logging.info(json.dumps(results))

        server.close_connection(bot_1.connection())
        server.close_connection(bot_2.connection())
        self.gameRecord = []
        self.bots.clear()

    def run(self):
        logging.info("Starting Battle: " + self.name)
        self.passedRounds = 0
        self.fileLogName = datetime.now().strftime("%d_%m_%Y_%H_%M_%S.log")
        self.fileHandle = open(self.fileLogName, 'a+')
        while server.closed is False and self.passedRounds < rules.numberOfRounds:
            try:
                self.runRound()
                self.concludeTurn()
            except OSError:
                bot_1, bot_2 = self.bots[0], self.bots[1]
                server.close_connection(bot_1.connection())
                server.close_connection(bot_2.connection())
                self.bots.clear()
                self.bot_id = 0
                break

        self.concludeGame()
        self.fileHandle.close()
        logging.info("Exiting " + self.name)


HOST = 'localhost'
PORT = 21000
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(message)s')

if __name__ == '__main__':
    logging.info('starting...')
    greetings = '-----<<<Battle.Server>>>-----\r\n---<<<CaptureTheNetwork>>>---\r\n'
    server = SelectorServer(greetings, host=HOST, port=PORT)
    thread1 = botDispachThread(1, "Dispatcher", server)
    thread1.start()
    try:
        server.serve_forever()
        logging.info('line after server start')
    except KeyboardInterrupt:
        pass
    server.close()
    thread1.join()
