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
    """
    Class used to async send data to bot.
    It is created to give equal chance to both bots.
    """
    def __init__(self, bot):
        threading.Thread.__init__(self)
        self.__bot = bot
        self.__deadline = time.time() + 3

    def run(self):
        global trigger
        while not trigger and time.time() < self.__deadline:
            time.sleep(0.0001)
        self.__bot.sendMessage('Command>')


class Battleground(threading.Thread):
    """
    Class responsible for handle bot battle.
    Object of this call do all operations required to come up with a winner.
    """
    def __init__(self, threadID, name, server, bot_1, bot_2):
        threading.Thread.__init__(self)
        self.__threadID = threadID
        self.__name = name
        self.__server = server
        self.__bots = [bot_1, bot_2]
        self.__timestamp = time.time()
        self.__passedRounds = 0
        self.__fileLogName = ''
        self.__gameRecord = []

    def saveData(self):
        """
        Method responsible for save battle data to file on disk.
        """
        self.__fileLogName = f'{self.__threadID}.json'
        Path("./history/games/").mkdir(parents=True, exist_ok=True)
        with open(f'./history/games/{self.__fileLogName}', 'w') as file:
            file.writelines(json.dumps(self.__gameRecord, sort_keys=True, indent=4))

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
            data[gff.GAME_ID.value] = self.__threadID
            data[gff.BOT_1.value][gff.BOT_NAME.value] = self.__bots[0].name()
            data[gff.BOT_1.value][gff.BOT_POINTS.value] = self.__bots[0].points()
            data[gff.BOT_2.value][gff.BOT_NAME.value] = self.__bots[1].name()
            data[gff.BOT_2.value][gff.BOT_POINTS.value] = self.__bots[1].points()
            data[gff.ROUNDS.value] = self.__passedRounds
            data[gff.DATE.value] = datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
            game_list.append(data)
            file.writelines(json.dumps(game_list, sort_keys=True, indent=4) + '\n')

    def runRound(self):
        """
        Method responsible for round control and calculation of round result.
        Here request for move is send to both bots.
        """
        global trigger
        threads = []
        self.__timestamp = time.time()
        for bot in self.__bots:
            bot.putMethod('NOP()', time.time(), False)
            threads.append(Sender(bot))
            threads[len(threads) - 1].start()
        trigger = True
        time.sleep(0.001)
        deadline = time.time() + rules.timeOfRound / 1000
        while time.time() < deadline:
            data = self.__server.getData()
            cData = copy.copy(data)
            timestamp = time.time()
            for bot_address, method in cData.items():
                for bot in self.__bots:
                    if bot.connection().getpeername() == bot_address:
                        bot.putMethod(method, timestamp)
                        del data[bot_address]
                        break
            time.sleep(0.001)
        trigger = False
        self.__passedRounds += 1

    def determineWinner(self):
        """
        Helper method used to calculate round winner
        :return: RoundWinner enum
        """
        bot_1, bot_2 = self.__bots[0], self.__bots[1]
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
        """
        Helper method used to determinate which bot will have advantage next round
        :return: RoundAdvantage enum
        """
        bot_1, bot_2 = self.__bots[0], self.__bots[1]
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
        """
        Helper method used to prepare messages with data about round
        :param summary: Json object with round summary
        :return: Two json object which are messages for bots
        """
        msg_1 = copy.copy(summary)
        msg_2 = copy.copy(summary)

        msg_1[bmf.BOT_1.value] = self.__bots[0].toJSON(self.__timestamp)
        msg_1[bmf.BOT_2.value] = self.__bots[1].toJSON(self.__timestamp)

        msg_2[bmf.BOT_1.value] = self.__bots[1].toJSON(self.__timestamp)
        msg_2[bmf.BOT_2.value] = self.__bots[0].toJSON(self.__timestamp)

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
        """
        Method responsible for preparation and sending messages with data about passed round
        """
        if len(self.__bots) != 2:
            return

        summary = tree()
        summary[bmf.TIME.value] = datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
        summary[bmf.WINNER.value] = self.determineWinner()
        summary[bmf.ADVANTAGE.value] = self.deremineAdvantage()
        summary[bmf.ROUND.value] = str(self.__passedRounds) + '/' + str(rules.numberOfRounds)
        msg_1, msg_2 = self.prepareBotMessages(summary)

        self.__bots[0].sendMessage(json.dumps(msg_1))
        self.__bots[1].sendMessage(json.dumps(msg_2))
        self.__gameRecord.append(msg_1)
        logging.info(json.dumps(summary))

    def cleanAfterGame(self):
        """
        Method used to clean up after bot battle ends
        :return:
        """
        for bot in self.__bots:
            self.__server.closeConnection(bot.connection())
        self.__gameRecord = []
        self.__bots.clear()

    def concludeGame(self):
        """
        Method responsible for preparation and sending messages with summary after battle.
        It also save data about game and clean up remains
        """
        if len(self.__bots) != 2:
            return

        bots = self.__bots
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

        self.saveData()
        self.cleanAfterGame()

    def run(self):
        """
        Main method of class. Responsible for logic flow of battles.
        """
        logging.info("Starting Battle: " + self.__name)
        self.__passedRounds = 0
        while self.__server.closed is False and self.__passedRounds < rules.numberOfRounds:
            try:
                self.runRound()
                self.concludeTurn()
            except OSError:
                self.cleanAfterGame()
                break

        self.concludeGame()
        logging.info("Exiting " + self.__name)
