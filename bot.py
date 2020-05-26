import time
from collections import defaultdict

import rules
from enumeration import Method, BotField


class Bot:
    """
    Class is used to represent a bot.
    It is responsible for handling all operation related with bot.
    """
    def __init__(self, conn, bot_id, name):
        self.__id = bot_id
        self.__conn = conn
        self.__name = name
        self.__prize_points = 0
        self.__advantage = False
        self.__timestamp = time.time()
        self.__method = Method.NOP
        self.sendMessage('Name?')

    def __tree(self):
        return defaultdict(self.__tree)

    def toJSON(self, timestamp):
        """
        Method used to serialize bot data to json format
        :param timestamp: Time stamp of serialization process
        :return: Most important fields from class in json format
        """
        bot_as_json = self.__tree()
        bot_as_json[BotField.NAME.value] = self.name()
        bot_as_json[BotField.USED.value] = rules.methodToName[self.method()]
        bot_as_json[BotField.TIME.value] = round(self.timestamp() - timestamp, 4)
        bot_as_json[BotField.POINTS.value] = self.points()
        return bot_as_json

    def sendMessage(self, message):
        """
        Method used to send a message to bot.
        :param message: Message with data which needs to be send to bot
        """
        self.__conn.send(message)

    def method(self):
        """
        Getter for bot method field / move of chose
        :return: Enumerator of Method class
        """
        return self.__method

    def points(self):
        """
        Getter for bot sum of points
        :return: Integer with all point gained by bot
        """
        return self.__prize_points

    def advantage(self):
        """
        Getter for bot advantage field
        :return: Boolean value. True if bot has advantage / False otherwise
        """
        return self.__advantage

    def putAdvantage(self, advantage):
        """
        Setter for advantage field of bot
        :param advantage: True / False boolean value
        """
        self.__advantage = advantage

    def putName(self, name):
        """
        Setter for name field of bot
        :param name: String object with name of bot
        """
        self.__name = name

    def name(self):
        """
        Getter of name field of bot class
        :return: String object containing bots name
        """
        return self.__name

    def id(self):
        """
        Getter of order number field of bot class
        :return: Integer with order number
        """
        return self.__id

    def connection(self):
        """
        Getter for connection field of bot class
        :return: SelectorServer Connection object
        """
        return self.__conn

    def timestamp(self):
        """
        Getter of timestamp field of bot class
        :return: Floating point number as timestamp representation
        """
        return self.__timestamp

    def addPrize(self):
        """
        Method responsible for adding points to bot
        """
        self.__prize_points += rules.methodToPrize[self.__method]

    def putMethod(self, method, timestamp, log=True):
        """
        Method responsible for assign move / method to bot
        :param method: Enum of Method
        :param timestamp: time stamp of method call
        :param log: flag used to log additional debug information
        """
        self.__timestamp = timestamp
        self.__method = Method.NOP
        if rules.nameToMethod.get(method, 'NA') != 'NA':
            self.__method = rules.nameToMethod[method]

        if log:
            self.sendMessage('Command: ' + rules.methodToName[self.__method])
