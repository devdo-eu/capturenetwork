import logging
import threading
import copy


class Namesaker(threading.Thread):
    def __init__(self, bot, server):
        threading.Thread.__init__(self)
        self.server = server
        self.bot = bot
        self.run()

    def run(self):
        named = False
        while not named:
            data = self.server.get_data()
            cData = copy.copy(data)
            for k, v in cData.items():
                try:
                    if self.bot.connection().getpeername() == k:
                        self.bot.putName(v[:-1])
                        logging.info(f'Namesaker: Bot introduced himself as {v[:-1]}')
                        del data[k]
                        named = True
                except OSError:
                    named = True
