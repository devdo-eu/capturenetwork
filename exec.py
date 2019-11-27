# -*- coding: utf-8 -*-
"""
Created on Thu Nov 21 19:32:07 2019

@author: Grzesiek-UC
"""

from TCP_Server import SelectorServer
import logging
import threading
import time

class myThread (threading.Thread):
   def __init__(self, threadID, name, server):
      threading.Thread.__init__(self)
      self.threadID = threadID
      self.name = name
      self.server = server
   def run(self):
      print ("Starting " + self.name)
      while server.closed == False:
          data = server.getData()
          if len(data):
              names = data.keys()
              if data[names[0]] == 'takeover\r\n':
                  logging.info('good')
              logging.info('got {} data: {!r}'.format(len(data), str(data)))
          time.sleep(1)
      print ("Exiting " + self.name)

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