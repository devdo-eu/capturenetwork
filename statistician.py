"""@package statistician
Package contains Statistician class used for gathering all statistic data from battle.
"""
import json
import rules
from copy import copy
from pathlib import Path
from enumeration import RoundWinner as rw
from enumeration import RoundAdvantage as ra
from collections import defaultdict


def tree(): return defaultdict(tree)


GENERAL = 'GENERAL'
NAME = 'NAME'
STATISTICS = 'STATISTICS'
TIME = 'Time'
DRAW = 'Draw'


class StatisticBank:

    def __init__(self, name, container):
        self.round_won_by = tree()
        self.advantage_after_round = tree()
        self.methods_used = tree()
        self.methods_used_per_round = []
        self.won_with_methods = tree()
        self.won_with_methods_per_round = []
        self.lost_with_methods = tree()
        self.lost_with_methods_per_round = []
        self.points_earned_with_method = tree()
        self.stats_list = {1: self.methods_used, 2: self.methods_used_per_round, 3: self.won_with_methods,
                           4: self.won_with_methods_per_round, 5: self.lost_with_methods,
                           6: self.lost_with_methods_per_round, 7: self.points_earned_with_method}
        self.__name = name
        for connect, stat in container.stats_list.items():
            temp = tree()
            temp[NAME] = self.__name
            temp[STATISTICS] = self.stats_list[connect]
            stat.append(copy(temp))

        for method in rules.methodsAsStrings:
            self.methods_used[method] = 0
            self.won_with_methods[method] = 0
            self.lost_with_methods[method] = 0
            self.points_earned_with_method[method] = 0


class Statistician:
    """
    Class contains all the methods responsible for the logic
    that gathers statistic data
    """

    def __init__(self, bot1_name, bot2_name, game_id):

        self.method_used_stats = []
        self.methods_used_per_round_stats = []
        self.won_with_methods_stats = []
        self.won_with_methods_per_round_stats = []
        self.lost_with_methods_stats = []
        self.lost_with_methods_per_round_stats = []
        self.points_earned_with_method_stats = []

        self.stats_list = {1: self.method_used_stats, 2: self.methods_used_per_round_stats,
                           3: self.won_with_methods_stats, 4: self.won_with_methods_per_round_stats,
                           5: self.lost_with_methods_stats, 6: self.lost_with_methods_per_round_stats,
                           7: self.points_earned_with_method_stats}

        self.__bot1_name = bot1_name
        self.__bot2_name = bot2_name
        self.__game_id = game_id
        self.__round = 0
        self.__bank = {GENERAL: StatisticBank(GENERAL, self),
                       self.__bot1_name: StatisticBank(self.__bot1_name, self),
                       self.__bot2_name: StatisticBank(self.__bot2_name, self)}

        self.__bank[GENERAL].round_won_by[DRAW] = 0
        self.__bank[GENERAL].round_won_by[self.__bot1_name] = 0
        self.__bank[GENERAL].round_won_by[self.__bot2_name] = 0

        self.__bank[GENERAL].advantage_after_round[TIME] = 0
        self.__bank[GENERAL].advantage_after_round[self.__bot1_name] = 0
        self.__bank[GENERAL].advantage_after_round[self.__bot2_name] = 0

        self.__stats = {'round_won_by': self.__bank[GENERAL].round_won_by,
                        'advantage_after_round': self.__bank[GENERAL].advantage_after_round,
                        'method_used': self.method_used_stats,
                        'method_used_per_round': self.methods_used_per_round_stats,
                        'won_with_methods': self.won_with_methods_stats,
                        'won_with_methods_per_round': self.won_with_methods_per_round_stats,
                        'lost_with_methods': self.lost_with_methods_stats,
                        'lost_with_methods_per_round': self.lost_with_methods_per_round_stats,
                        'points_earned_with_method': self.points_earned_with_method_stats}

    def __updateRoundWonBy(self, winner):
        """
        Private helper method used to updating round winner statistics
        :param winner: RoundWinner from enumeration package with information about round winner
        """
        if winner is rw.DRAW:
            self.__bank[GENERAL].round_won_by[DRAW] += 1
        elif winner is rw.BOT_1:
            self.__bank[GENERAL].round_won_by[self.__bot1_name] += 1
        else:
            self.__bank[GENERAL].round_won_by[self.__bot2_name] += 1

    def __updateWonLostByMethod(self, bot1_method, bot2_method, winner):
        """
        Private helper method used to update stats related with won and lost with method
        :param bot1_method: String with method used by BOT1
        :param bot2_method: String with method used by BOT2
        :param winner: RoundWinner from enumeration package with information about round winner
        """
        bot1 = self.__bank[self.__bot1_name]
        bot2 = self.__bank[self.__bot2_name]
        if winner is rw.BOT_1:
            bot1.won_with_methods[bot1_method] += 1
            bot2.lost_with_methods[bot2_method] += 1
        elif winner is rw.BOT_2:
            bot1.lost_with_methods[bot1_method] += 1
            bot2.won_with_methods[bot2_method] += 1

        bot1.won_with_methods_per_round.append(copy(bot1.won_with_methods))
        bot1.lost_with_methods_per_round.append(copy(bot1.lost_with_methods))
        bot2.won_with_methods_per_round.append(copy(bot2.won_with_methods))
        bot2.lost_with_methods_per_round.append(copy(bot2.lost_with_methods))

    def __updatePointsEarnedWithMethod(self, bot1_method, bot2_method, winner):
        """
        Private helper method used to update stats related with points earned with methods
        :param bot1_method: String with method used by BOT1
        :param bot2_method: String with method used by BOT2
        :param winner: RoundWinner from enumeration package with information about round winner
        """
        if winner is rw.BOT_1:
            points = rules.methodToPrize[rules.nameToMethod[bot1_method]]
            self.__bank[self.__bot1_name].points_earned_with_method[bot1_method] += points
        elif winner is rw.BOT_2:
            points = rules.methodToPrize[rules.nameToMethod[bot2_method]]
            self.__bank[self.__bot2_name].points_earned_with_method[bot2_method] += points

    def __updateAdvantageAfterRounds(self, advantage):
        """
        Private helper method used to update stats related with getting advantage after round
        :param advantage: RoundAdvantage from enumeration package with information about round advantage
        """
        if advantage is ra.TIME:
            self.__bank[GENERAL].advantage_after_round[TIME] += 1
        elif advantage is ra.BOT_1:
            self.__bank[GENERAL].advantage_after_round[self.__bot1_name] += 1
        else:
            self.__bank[GENERAL].advantage_after_round[self.__bot2_name] += 1

    def __updateMethodsUsed(self, bot1_method, bot2_method):
        """
        Private helper method used to update stats related with stats about methods used in game
        :param bot1_method: String with method used by BOT1
        :param bot2_method: String with method used by BOT2
        """
        bot1 = self.__bank[self.__bot1_name]
        bot2 = self.__bank[self.__bot2_name]
        bot1.methods_used[bot1_method] += 1
        bot2.methods_used[bot2_method] += 1

        for method in rules.methodsAsStrings:
            self.__bank[GENERAL].methods_used[method] = bot1.methods_used[method] + bot2.methods_used[method]

        self.__bank[GENERAL].methods_used_per_round.append(copy(self.__bank[GENERAL].methods_used))
        bot1.methods_used_per_round.append(copy(bot1.methods_used))
        bot2.methods_used_per_round.append(copy(bot2.methods_used))

    def updateStats(self, bot1_method, bot2_method, winner, advantage):
        """
        Public method used to update all statistics gathered in game
        :param bot1_method: String with method used by BOT1
        :param bot2_method: String with method used by BOT2
        :param winner: RoundWinner from enumeration package with information about round winner
        :param advantage:
        """
        self.__round += 1
        self.__updateRoundWonBy(winner)
        self.__updateAdvantageAfterRounds(advantage)
        self.__updateMethodsUsed(bot1_method, bot2_method)
        self.__updateWonLostByMethod(bot1_method, bot2_method, winner)
        self.__updatePointsEarnedWithMethod(bot1_method, bot2_method, winner)

    def dumpStatistics(self):
        """
        Public method used to trigger saving all gathered data to files
        """
        path = f"./history/games/{self.__game_id}/stats"
        Path(path).mkdir(parents=True, exist_ok=True)
        bot1 = self.__bank[self.__bot1_name]
        bot2 = self.__bank[self.__bot2_name]
        general = self.__bank[GENERAL]

        for method in rules.methodsAsStrings:
            general.won_with_methods[method] = bot1.won_with_methods[method] + bot2.won_with_methods[method]
            general.lost_with_methods[method] = bot1.lost_with_methods[method] + bot2.lost_with_methods[method]
            general.points_earned_with_method[method] = bot1.points_earned_with_method[method] + \
                                                        bot2.points_earned_with_method[method]

        for name, data in self.__stats.items():
            with open(f'{path}/{name}.json', 'w') as file:
                file.writelines(json.dumps(data, sort_keys=True, indent=4))
