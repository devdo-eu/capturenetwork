# -*- coding: utf-8 -*-
"""
Created on Thu Nov 21 19:32:07 2019

@author: Grzesiek-UC
"""
from TCP_Server import SelectorServer
import logging
import argparse
from dispatcher import Dispatcher
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(message)s')


def parse():
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', dest='host', type=str, default='localhost', help="defines server host")
    parser.add_argument('--port', dest='port', type=int, default=21000, help="defines server port number")
    return parser.parse_args()


if __name__ == '__main__':
    args = parse()
    logging.info(f'Server at {args.host}:{args.port}')
    logging.info('Battle.Server: Starting...')
    greetings = '-----<<<Battle.Server>>>-----\r\n---<<<CaptureTheNetwork>>>---\r\n'
    server = SelectorServer(greetings, host=args.host, port=args.port)
    thread1 = Dispatcher(1, "Dispatcher", server)
    thread1.start()
    try:
        server.serve_forever()
        logging.info('line after server start')
    except KeyboardInterrupt:
        pass
    server.close()
    thread1.join()
