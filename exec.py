# -*- coding: utf-8 -*-
"""
Created on Thu Nov 21 19:32:07 2019

@author: Grzesiek-UC
"""

from TCP_Server import SelectorServer
import logging
import threading
import time
import bot
import rules

class myThread(threading.Thread):
    def __init__(self, threadID, name, server):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.server = server
        self.bot_id = 0
        self.bots = []

    def logBots(self):
        data = server.getData()
        while len(data):
            item = data.popitem()
            if item[1][:-2] == 'takeover':
                conn_index = 0
                for conn in server.conns:
                    if conn.getpeername() == item[0]:
                        server.conns.pop(conn_index)
                        new_bot = bot.Bot(conn, self.bot_id, 'BOT_' + str(self.bot_id))
                        self.bots.append(new_bot)
                        self.bot_id += 1
                    conn_index += 1
            else:
                for tbot in self.bots:
                    if tbot.connection().getpeername() == item[0]:
                        tbot.putName(item[1][:-2])
                for conn in server.conns:
                    if conn.getpeername() == item[0]:
                        server.send_to_conn(item[0], 'Access denied\r\n')
                        server.close_connection(conn)
                        server.conns.remove(conn)
        time.sleep(1)

    def runRound(self):
        for tbot in self.bots:
            tbot.sendMessage('Command>\r\n')
        time.sleep(rules.timeOfRound / 1000)
        data = server.getData()
        while len(data):
            item = data.popitem()
            for tbot in self.bots:
                if tbot.connection().getpeername() == item[0]:
                    if item[1][:5] == 'NAME(' and item[1][-3:-2] == ')':
                        tbot.putName(item[1][5:-3])
                    else:
                        tbot.putMethod(item[1][:-2])
            for conn in server.conns:
                if conn.getpeername() == item[0]:
                    server.send_to_conn(item[0], 'Access denied - Battle in progress\r\n')
                    server.close_connection(conn)
                    server.conns.remove(conn)

    def run(self):
        print("Starting " + self.name)
        while server.closed is False and self.bot_id < 2:
            self.logBots()

        while server.closed is False:
            self.runRound()

        print("Exiting " + self.name)


HOST = 'localhost'
PORT = 21000
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(message)s')

if __name__ == '__main__':
    logging.info('starting')
    greetings = '-----<<<Battle.Server>>>-----\r\n---<<<CaptureTheNetwork>>>---\r\n'
    server = SelectorServer(greetings, host=HOST, port=PORT)
    thread1 = myThread(1, "Game Logic Thread", server)
    thread1.start()
    try:
        server.serve_forever()
        logging.info('line after server start')
    except KeyboardInterrupt:
        pass
    server.close()
    thread1.join()
