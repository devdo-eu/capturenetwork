import logging
import threading
import copy
import time


class Namesaker(threading.Thread):
    def __init__(self, bot, server):
        threading.Thread.__init__(self)
        self.server = server
        self.bot = bot

    def run(self):
        named = False
        deadline = time.time() + 5
        while not named and time.time() < deadline:
            data = self.server.getData()
            cData = copy.copy(data)
            for peer_address, name in cData.items():
                try:
                    if self.bot.connection().getpeername() == peer_address:
                        self.bot.putName(name)
                        logging.info(f'Namesaker: Bot introduced himself as {name}')
                        del data[peer_address]
                        named = True
                except OSError:
                    named = True
        if not named:
            logging.info('Bot stay without name...')
