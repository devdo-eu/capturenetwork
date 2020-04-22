
from collections import defaultdict
import logging
import threading
import time
import rules
import json
import copy
from datetime import datetime
from pathlib import Path
from enumeration import RoundWinner, RoundAdvantage


def tree(): return defaultdict(tree)

trigger = False

class Sender(threading.Thread):
    def __init__(self, bot):
        threading.Thread.__init__(self)
        self.bot = bot
        self.deadline = time.time() + 3

    def run(self):
        global trigger
        while not trigger and time.time() < self.deadline:
            time.sleep(0.0001)
        self.bot.sendMessage('Command>\r\n')


class Battleground(threading.Thread):
    def __init__(self, threadID, name, server, bot_1, bot_2):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.server = server
        self.bots = [bot_1, bot_2]
        self.timestamp = time.time()
        self.passedRounds = 0
        self.fileLogName = ''
        self.gameRecord = []

    def saveData(self, bot_1, bot_2):
        self.fileLogName = f'{self.threadID}.json'
        Path("./games/").mkdir(parents=True, exist_ok=True)
        game_json = tree()
        game_json['ROUNDS'] = []
        for round in self.gameRecord:
            game_json['ROUNDS'].append(round)
        with open('games/' + self.fileLogName, 'w') as file:
            file.writelines(json.dumps(game_json, sort_keys=True, indent=4))

        try:
            with open('game_list.json', 'r') as file:
                game_list = ''
                for line in file:
                    game_list += line
                game_list = json.loads(game_list)
        except FileNotFoundError as e:
            logging.info('No game_list.json file. Creating file.')
            game_list = tree()
            game_list['GAMES'] = []
        except json.JSONDecodeError as e:
            logging.info('Bad format inside game_list.json file.')
            game_list = tree()
            game_list['GAMES'] = []

        with open('game_list.json', 'w') as file:
            data = tree()
            data['GAME_ID'] = self.threadID
            data['BOT_1']['NAME'] = bot_1.name()
            data['BOT_1']['POINTS'] = bot_1.points()
            data['BOT_2']['NAME'] = bot_2.name()
            data['BOT_2']['POINTS'] = bot_2.points()
            data['ROUNDS'] = self.passedRounds
            data['DATE'] = datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
            game_list['GAMES'].append(data)
            file.writelines(json.dumps(game_list, sort_keys=True, indent=4) + '\n')

    def runRound(self):
        global trigger
        time.sleep(0.01)
        for bot in self.bots:
            bot.putMethod('NOP()', time.time(), False)
            Sender(bot).start()
        self.timestamp = time.time()
        trigger = True
        deadline = time.time() + rules.timeOfRound / 1000
        while time.time() < deadline:
            data = self.server.get_data()
            cData = copy.copy(data)
            timestamp = time.time()
            for k, v in cData.items():
                for bot in self.bots:
                    if bot.connection().getpeername() == k:
                        bot.putMethod(v[:-2], timestamp)
                        del data[k]
                        break
            time.sleep(0.001)
        trigger = False
        self.passedRounds += 1

    def determineWinner(self):
        bot_1, bot_2 = self.bots[0], self.bots[1]
        result_1 = rules.methodToMethodResult[bot_1.method()][bot_2.method()]
        winner = RoundWinner.DRAW

        if result_1 is rules.Result.FASTER_WINNER:
            if bot_1.advantage():
                result_1 = rules.Result.WIN
            elif bot_2.advantage():
                result_1 = rules.Result.LOSE
            else:
                if bot_1.timestamp() < bot_2.timestamp():
                    result_1 = rules.Result.WIN
                else:
                    result_1 = rules.Result.LOSE

        if result_1 is rules.Result.WIN:
            bot_1.addPrize()
            winner = RoundWinner.BOT_1
        elif result_1 is rules.Result.LOSE:
            bot_2.addPrize()
            winner = RoundWinner.BOT_2
        return winner

    def deremineAdvantage(self):
        bot_1, bot_2 = self.bots[0], self.bots[1]
        advantage_1 = rules.methodToMethodAdvantage[bot_1.method()][bot_2.method()]
        bot_1.putAdvantage(False)
        bot_2.putAdvantage(False)
        adv = RoundAdvantage.TIME
        if advantage_1 is rules.Advantage.GAIN:
            bot_1.putAdvantage(True)
            bot_2.putAdvantage(False)
            adv = RoundAdvantage.BOT_1
        elif advantage_1 is rules.Advantage.LOST:
            bot_1.putAdvantage(False)
            bot_2.putAdvantage(True)
            adv = RoundAdvantage.BOT_2
        return adv

    def prepareBotMessages(self, summary):
        msg_1 = copy.copy(summary)
        msg_2 = copy.copy(summary)
        msg_1['BOT_1'], msg_1['BOT_2'] = self.bots[0].toJSON(self.timestamp), self.bots[1].toJSON(self.timestamp)
        msg_2['BOT_1'], msg_2['BOT_2'] = self.bots[1].toJSON(self.timestamp), self.bots[0].toJSON(self.timestamp)

        if msg_2['ADVANTAGE'] == RoundWinner.BOT_2:
            msg_2['ADVANTAGE'] = 1
        elif msg_2['ADVANTAGE'] == RoundWinner.BOT_1:
            msg_2['ADVANTAGE'] = 2
        return msg_1, msg_2

    def concludeTurn(self):
        if len(self.bots) != 2:
            return

        summary = tree()
        summary['TIME'] = datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
        summary['WINNER'], summary['ADVANTAGE'] = self.determineWinner(), self.deremineAdvantage()
        summary['ROUND'] = str(self.passedRounds) + '/' + str(rules.numberOfRounds)
        msg_1, msg_2 = self.prepareBotMessages(summary)

        self.bots[0].sendMessage(json.dumps(msg_1) + '\r\n')
        self.bots[1].sendMessage(json.dumps(msg_2) + '\r\n')
        self.gameRecord.append(msg_1)
        logging.info(json.dumps(summary))

    def cleanAfterGame(self):
        for bot in self.bots:
            self.server.close_connection(bot.connection())
        self.gameRecord = []
        self.bots.clear()

    def concludeGame(self):
        if len(self.bots) != 2:
            return

        bots = self.bots
        results = tree()
        shortcut = results['WINNER']
        if bots[0].points() > bots[1].points():
            shortcut['ID'], shortcut['NAME'], shortcut['POINTS'] = RoundWinner.BOT_1, bots[0].name(), bots[0].points()
        elif bots[0].points() < bots[1].points():
            shortcut['ID'], shortcut['NAME'], shortcut['POINTS'] = RoundWinner.BOT_2, bots[1].name(), bots[1].points()
        else:
            shortcut['ID'], shortcut['NAME'], shortcut['POINTS'] = RoundWinner.DRAW, '-', 0

        bots[0].sendMessage(json.dumps(results))
        bots[1].sendMessage(json.dumps(results))
        logging.info(json.dumps(results))

        self.saveData(bots[0], bots[1])
        self.cleanAfterGame()

    def run(self):
        logging.info("Starting Battle: " + self.name)
        self.passedRounds = 0
        while self.server.closed is False and self.passedRounds < rules.numberOfRounds:
            try:
                self.runRound()
                self.concludeTurn()
            except OSError:
                self.cleanAfterGame()
                break

        self.concludeGame()
        logging.info("Exiting " + self.name)
