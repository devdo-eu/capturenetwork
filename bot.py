import time
from enumeration import Method
from collections import defaultdict
import rules


class Bot:
    def __init__(self, conn, iden, name):
        self.__id = iden
        self.__conn = conn
        self.__name = name
        self.__prize_points = 0
        self.__advantage = False
        self.__timestamp = time.time()
        self.__method = Method.NOP
        self.sendMessage('Name?\r\n')

    def __tree(self): return defaultdict(self.__tree)

    def toJSON(self, timestamp):
        ret = self.__tree()
        ret['NAME'] = self.name()
        ret['USED'] = rules.methodToName[self.method()]
        ret['TIME'] = round(self.timestamp() - timestamp, 4)
        ret['POINTS'] = self.points()
        return ret

    def sendMessage(self, message):
        self.__conn.send(message.encode('utf-8'))

    def method(self):
        return self.__method

    def points(self):
        return self.__prize_points

    def advantage(self):
        return self.__advantage

    def putAdvantage(self, advantage):
        self.__advantage = advantage

    def putName(self, name):
        self.__name = name

    def name(self):
        return self.__name

    def id(self):
        return self.__id

    def connection(self):
        return self.__conn

    def timestamp(self):
        return self.__timestamp

    def addPrize(self):
        self.__prize_points += rules.methodToPrize[self.__method]

    def putMethod(self, method, timestamp, log=True):
        self.__timestamp = timestamp
        self.__method = Method.NOP
        if rules.nameToMethod.get(method, 'NA') != 'NA':
            self.__method = rules.nameToMethod[method]
        if log:
            self.sendMessage('Command: ' + rules.methodToName[self.__method] + '\r\n')
