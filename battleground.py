
from collections import defaultdict
import logging
import threading
import time
import bot
import rules
import json
import copy
from datetime import datetime
from pathlib import Path


def tree(): return defaultdict(tree)


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
        with open('games/' + self.fileLogName, 'a+') as file:
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
        self.timestamp = time.time()
        for tbot in self.bots:
            tbot.putMethod('NOP()', False)
            time.sleep(rules.timeOfRound / 3000)
            tbot.sendMessage('Command>\r\n')
        time.sleep(rules.timeOfRound * 2 / 3000)
        data = self.server.get_data()
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
        summary['TIME'] = datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
        summary['WINNER'], summary['ADVANTAGE'] = winner, adv
        summary['ROUND'] = str(self.passedRounds) + '/' + str(rules.numberOfRounds)

        msg_1 = copy.copy(summary)
        msg_2 = copy.copy(summary)
        msg_1['BOT_1'], msg_1['BOT_2'] = bot_1.toJSON(self.timestamp), bot_2.toJSON(self.timestamp)
        msg_2['BOT_1'], msg_2['BOT_2'] = bot_2.toJSON(self.timestamp), bot_1.toJSON(self.timestamp)

        bot_1.sendMessage(json.dumps(msg_1) + '\r\n')
        bot_2.sendMessage(json.dumps(msg_2) + '\r\n')
        self.gameRecord.append(msg_1)
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

        self.saveData(bot_1, bot_2)

        logging.info(json.dumps(results))
        self.server.close_connection(bot_1.connection())
        self.server.close_connection(bot_2.connection())
        self.gameRecord = []
        self.bots.clear()

    def run(self):
        logging.info("Starting Battle: " + self.name)
        self.passedRounds = 0
        while self.server.closed is False and self.passedRounds < rules.numberOfRounds:
            try:
                self.runRound()
                self.concludeTurn()
            except OSError:
                bot_1, bot_2 = self.bots[0], self.bots[1]
                self.server.close_connection(bot_1.connection())
                self.server.close_connection(bot_2.connection())
                self.bots.clear()
                break

        self.concludeGame()
        logging.info("Exiting " + self.name)
