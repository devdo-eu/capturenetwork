import logging
import threading
import copy
import time


class NameSaker(threading.Thread):
    """
    Class responsible for finding out the bot's name.
    """
    def __init__(self, bot, server):
        threading.Thread.__init__(self)
        self.__server = server
        self.__bot = bot

    def run(self):
        named = False
        deadline = time.time() + 5
        while not named and time.time() < deadline:
            data = self.__server.getData()
            data_copy = copy.copy(data)
            for peer_address, name in data_copy.items():
                try:
                    if self.__bot.connection().getpeername() == peer_address:
                        self.__bot.putName(name)
                        logging.info(f'Namesaker: Bot introduced himself as {name}')
                        del data[peer_address]
                        named = True
                except OSError:
                    named = True
        if not named:
            logging.info('Bot stay without name...')
