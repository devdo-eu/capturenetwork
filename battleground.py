import copy
import json
import logging
import threading
import time
from collections import defaultdict
from datetime import datetime
from pathlib import Path

import rules
from enumeration import BotMessageField as bmf
from enumeration import GamesListFileField as gff
from enumeration import RoundAdvantage as ra
from enumeration import RoundWinner as rw


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
        self.bot.sendMessage('Command>')


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
        Path("./history/games/").mkdir(parents=True, exist_ok=True)
        with open(f'./history/games/{self.fileLogName}', 'w') as file:
            file.writelines(json.dumps(self.gameRecord, sort_keys=True, indent=4))

        try:
            with open('./history/game_list.json', 'r') as file:
                game_list = ''
                for line in file:
                    game_list += line
                game_list = json.loads(game_list)
        except (FileNotFoundError, json.JSONDecodeError) as error:
            if isinstance(error, FileNotFoundError):
                logging.info('No game_list.json file. Creating file.')
            else:
                logging.info('Bad format inside game_list.json file.')
            game_list = []

        with open('./history/game_list.json', 'w') as file:
            data = tree()
            data[gff.GAME_ID.value] = self.threadID
            data[gff.BOT_1.value][gff.BOT_NAME.value] = bot_1.name()
            data[gff.BOT_1.value][gff.BOT_POINTS.value] = bot_1.points()
            data[gff.BOT_2.value][gff.BOT_NAME.value] = bot_2.name()
            data[gff.BOT_2.value][gff.BOT_POINTS.value] = bot_2.points()
            data[gff.ROUNDS.value] = self.passedRounds
            data[gff.DATE.value] = datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
            game_list.append(data)
            file.writelines(json.dumps(game_list, sort_keys=True, indent=4) + '\n')

    def runRound(self):
        global trigger
        threads = []
        self.timestamp = time.time()
        for bot in self.bots:
            bot.putMethod('NOP()', time.time(), False)
            threads.append(Sender(bot))
            threads[len(threads) - 1].start()
        trigger = True
        time.sleep(0.001)
        deadline = time.time() + rules.timeOfRound / 1000
        while time.time() < deadline:
            data = self.server.getData()
            cData = copy.copy(data)
            timestamp = time.time()
            for bot_address, method in cData.items():
                for bot in self.bots:
                    if bot.connection().getpeername() == bot_address:
                        bot.putMethod(method, timestamp)
                        del data[bot_address]
                        break
            time.sleep(0.001)
        trigger = False
        self.passedRounds += 1

    def determineWinner(self):
        bot_1, bot_2 = self.bots[0], self.bots[1]
        result_1 = rules.methodToMethodResult[bot_1.method()][bot_2.method()]
        winner = rw.DRAW

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
            winner = rw.BOT_1
        elif result_1 is rules.Result.LOSE:
            bot_2.addPrize()
            winner = rw.BOT_2
        return winner

    def deremineAdvantage(self):
        bot_1, bot_2 = self.bots[0], self.bots[1]
        advantage_1 = rules.methodToMethodAdvantage[bot_1.method()][bot_2.method()]
        bot_1.putAdvantage(False)
        bot_2.putAdvantage(False)
        adv = ra.TIME
        if advantage_1 is rules.Advantage.GAIN:
            bot_1.putAdvantage(True)
            bot_2.putAdvantage(False)
            adv = ra.BOT_1
        elif advantage_1 is rules.Advantage.LOST:
            bot_1.putAdvantage(False)
            bot_2.putAdvantage(True)
            adv = ra.BOT_2
        return adv

    def prepareBotMessages(self, summary):
        msg_1 = copy.copy(summary)
        msg_2 = copy.copy(summary)

        msg_1[bmf.BOT_1.value] = self.bots[0].toJSON(self.timestamp)
        msg_1[bmf.BOT_2.value] = self.bots[1].toJSON(self.timestamp)

        msg_2[bmf.BOT_1.value] = self.bots[1].toJSON(self.timestamp)
        msg_2[bmf.BOT_2.value] = self.bots[0].toJSON(self.timestamp)

        if msg_2[bmf.ADVANTAGE.value] == ra.BOT_2:
            msg_2[bmf.ADVANTAGE.value] = 1
        elif msg_2[bmf.ADVANTAGE.value] == ra.BOT_1:
            msg_2[bmf.ADVANTAGE.value] = 2

        if msg_2[bmf.WINNER.value] == rw.BOT_2:
            msg_2[bmf.WINNER.value] = 1
        elif msg_2[bmf.WINNER.value] == rw.BOT_1:
            msg_2[bmf.WINNER.value] = 2
        return msg_1, msg_2

    def concludeTurn(self):
        if len(self.bots) != 2:
            return

        summary = tree()
        summary[bmf.TIME.value] = datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
        summary[bmf.WINNER.value] = self.determineWinner()
        summary[bmf.ADVANTAGE.value] = self.deremineAdvantage()
        summary[bmf.ROUND.value] = str(self.passedRounds) + '/' + str(rules.numberOfRounds)
        msg_1, msg_2 = self.prepareBotMessages(summary)

        self.bots[0].sendMessage(json.dumps(msg_1))
        self.bots[1].sendMessage(json.dumps(msg_2))
        self.gameRecord.append(msg_1)
        logging.info(json.dumps(summary))

    def cleanAfterGame(self):
        for bot in self.bots:
            self.server.closeConnection(bot.connection())
        self.gameRecord = []
        self.bots.clear()

    def concludeGame(self):
        if len(self.bots) != 2:
            return

        bots = self.bots
        results = tree()
        shortcut = results[bmf.WINNER.value]
        if bots[0].points() > bots[1].points():
            shortcut[bmf.ID.value] = rw.BOT_1
            shortcut[bmf.NAME.value] = bots[0].name()
            shortcut[bmf.POINTS.value] = bots[0].points()
        elif bots[0].points() < bots[1].points():
            shortcut[bmf.ID.value] = rw.BOT_2
            shortcut[bmf.NAME.value] = bots[1].name()
            shortcut[bmf.POINTS.value] = bots[1].points()
        else:
            shortcut[bmf.ID.value] = rw.DRAW
            shortcut[bmf.NAME.value] = '-'
            shortcut[bmf.POINTS.value] = 0

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
