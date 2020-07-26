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


class Statistician:
    """
    Class contains all the methods responsible for the logic
    that gathers statistic data
    """

    def __init__(self, bot1_name, bot2_name, game_id):
        self.__bot1_name = bot1_name
        self.__bot2_name = bot2_name
        self.__game_id = game_id
        self.__round = 0

        self.__round_won_by = tree()
        self.__advantage_after_round = tree()
        self.__methods_used = tree()
        self.__methods_used_per_round = []
        self.__won_with_methods = tree()
        self.__lost_with_methods = tree()

        self.__bot1_methods_used = tree()
        self.__bot1_methods_used_per_round = []
        self.__bot1_won_with_methods = tree()
        self.__bot1_won_with_methods_per_round = []
        self.__bot1_lost_with_methods = tree()
        self.__bot1_lost_with_methods_per_round = []
        self.__bot1_points_earned_with_method = tree()

        self.__bot2_methods_used = tree()
        self.__bot2_methods_used_per_round = []
        self.__bot2_won_with_methods = tree()
        self.__bot2_won_with_methods_per_round = []
        self.__bot2_lost_with_methods = tree()
        self.__bot2_lost_with_methods_per_round = []
        self.__bot2_points_earned_with_method = tree()

        self.__stats = {}
        self.__initialize()

    def __initialize(self):
        """
        Private helper method used to initialize with 0 all data containers
        """
        self.__round_won_by['Draw'] = 0
        self.__round_won_by[self.__bot1_name] = 0
        self.__round_won_by[self.__bot2_name] = 0

        self.__advantage_after_round['Time'] = 0
        self.__advantage_after_round[self.__bot1_name] = 0
        self.__advantage_after_round[self.__bot2_name] = 0

        for method in rules.methodsAsStrings:
            self.__methods_used[method] = 0
            self.__won_with_methods[method] = 0
            self.__lost_with_methods[method] = 0

            self.__bot1_methods_used[method] = 0
            self.__bot1_won_with_methods[method] = 0
            self.__bot1_lost_with_methods[method] = 0
            self.__bot1_points_earned_with_method[method] = 0

            self.__bot2_methods_used[method] = 0
            self.__bot2_won_with_methods[method] = 0
            self.__bot2_lost_with_methods[method] = 0
            self.__bot2_points_earned_with_method[method] = 0

        self.__stats = {'round_won_by': self.__round_won_by,
                        'advantage_after_round': self.__advantage_after_round,
                        'method_used': self.__methods_used,
                        f'{self.__bot1_name}_method_used': self.__bot1_methods_used,
                        f'{self.__bot2_name}_method_used': self.__bot2_methods_used,
                        'method_used_per_round': self.__methods_used_per_round,
                        f'{self.__bot1_name}_method_used_per_round': self.__bot1_methods_used_per_round,
                        f'{self.__bot2_name}_method_used_per_round': self.__bot2_methods_used_per_round,
                        'won_with_methods': self.__won_with_methods,
                        'lost_with_methods': self.__lost_with_methods,
                        f'{self.__bot1_name}_won_with_methods': self.__bot1_won_with_methods,
                        f'{self.__bot1_name}_lost_with_methods': self.__bot1_lost_with_methods,
                        f'{self.__bot1_name}_won_with_methods_per_round': self.__bot1_won_with_methods_per_round,
                        f'{self.__bot1_name}_lost_with_methods_per_round': self.__bot1_lost_with_methods_per_round,
                        f'{self.__bot1_name}_points_earned_with_method': self.__bot1_points_earned_with_method,
                        f'{self.__bot2_name}_won_with_methods': self.__bot2_won_with_methods,
                        f'{self.__bot2_name}_lost_with_methods': self.__bot2_lost_with_methods,
                        f'{self.__bot2_name}_won_with_methods_per_round': self.__bot2_won_with_methods_per_round,
                        f'{self.__bot2_name}_lost_with_methods_per_round': self.__bot2_lost_with_methods_per_round,
                        f'{self.__bot2_name}_points_earned_with_method': self.__bot2_points_earned_with_method}

    def __update_round_won_by(self, winner):
        """
        Private helper method used to updating round winner statistics
        :param winner: RoundWinner from enumeration package with information about round winner
        """
        if winner is rw.DRAW:
            self.__round_won_by['Draw'] += 1
        elif winner is rw.BOT_1:
            self.__round_won_by[self.__bot1_name] += 1
        else:
            self.__round_won_by[self.__bot2_name] += 1

    def __update_won_lost_by_method(self, bot1_method, bot2_method, winner):
        """
        Private helper method used to update stats related with won and lost with method
        :param bot1_method: String with method used by BOT1
        :param bot2_method: String with method used by BOT2
        :param winner: RoundWinner from enumeration package with information about round winner
        """
        if winner is rw.BOT_1:
            self.__bot1_won_with_methods[bot1_method] += 1
            self.__bot2_lost_with_methods[bot2_method] += 1
        elif winner is rw.BOT_2:
            self.__bot1_lost_with_methods[bot1_method] += 1
            self.__bot2_won_with_methods[bot2_method] += 1

        self.__bot1_won_with_methods_per_round.append(copy(self.__bot1_won_with_methods))
        self.__bot1_lost_with_methods_per_round.append(copy(self.__bot1_lost_with_methods))
        self.__bot2_won_with_methods_per_round.append(copy(self.__bot2_won_with_methods))
        self.__bot2_lost_with_methods_per_round.append(copy(self.__bot2_lost_with_methods))

    def __update_points_earned_with_method(self, bot1_method, bot2_method, winner):
        """
        Private helper method used to update stats related with points earned with methods
        :param bot1_method: String with method used by BOT1
        :param bot2_method: String with method used by BOT2
        :param winner: RoundWinner from enumeration package with information about round winner
        """
        if winner is rw.BOT_1:
            points = rules.methodToPrize[rules.nameToMethod[bot1_method]]
            self.__bot1_points_earned_with_method[bot1_method] += points
        elif winner is rw.BOT_2:
            points = rules.methodToPrize[rules.nameToMethod[bot2_method]]
            self.__bot2_points_earned_with_method[bot2_method] += points

    def __update_advantage_after_rounds(self, advantage):
        """
        Private helper method used to update stats related with getting advantage after round
        :param advantage: RoundAdvantage from enumeration package with information about round advantage
        """
        if advantage is ra.TIME:
            self.__advantage_after_round['Time'] += 1
        elif advantage is ra.BOT_1:
            self.__advantage_after_round[self.__bot1_name] += 1
        else:
            self.__advantage_after_round[self.__bot2_name] += 1

    def __update_methods_used(self, bot1_method, bot2_method):
        """
        Private helper method used to update stats related with stats about methods used in game
        :param bot1_method: String with method used by BOT1
        :param bot2_method: String with method used by BOT2
        """
        self.__bot1_methods_used[bot1_method] += 1
        self.__bot2_methods_used[bot2_method] += 1

        for method in rules.methodsAsStrings:
            self.__methods_used[method] = self.__bot1_methods_used[method] + self.__bot2_methods_used[method]

        self.__methods_used_per_round.append(copy(self.__methods_used))
        self.__bot1_methods_used_per_round.append(copy(self.__bot1_methods_used))
        self.__bot2_methods_used_per_round.append(copy(self.__bot2_methods_used))

    def update_stats(self, bot1_method, bot2_method, winner, advantage):
        """
        Public method used to update all statistics gathered in game
        :param bot1_method: String with method used by BOT1
        :param bot2_method: String with method used by BOT2
        :param winner: RoundWinner from enumeration package with information about round winner
        :param advantage:
        """
        self.__round += 1
        self.__update_round_won_by(winner)
        self.__update_advantage_after_rounds(advantage)
        self.__update_methods_used(bot1_method, bot2_method)
        self.__update_won_lost_by_method(bot1_method, bot2_method, winner)
        self.__update_points_earned_with_method(bot1_method, bot2_method, winner)

    def dump_statistics(self):
        """
        Public method used to trigger saving all gathered data to files
        """
        path = f"./history/games/{self.__game_id}/stats"
        Path(path).mkdir(parents=True, exist_ok=True)

        for method in rules.methodsAsStrings:
            self.__won_with_methods[method] = self.__bot1_won_with_methods[method] + \
                                              self.__bot2_won_with_methods[method]
            self.__lost_with_methods[method] = self.__bot1_lost_with_methods[method] + \
                                               self.__bot2_lost_with_methods[method]

        for name, data in self.__stats.items():
            with open(f'{path}/{name}.json', 'w') as file:
                file.writelines(json.dumps(data, sort_keys=True, indent=4))
