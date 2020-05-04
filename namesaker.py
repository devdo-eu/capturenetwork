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
            for peer_address, name in cData.items():
                try:
                    if self.bot.connection().getpeername() == peer_address:
                        self.bot.putName(name)
                        logging.info(f'Namesaker: Bot introduced himself as {name}')
                        del data[peer_address]
                        named = True
                except OSError:
                    named = True
