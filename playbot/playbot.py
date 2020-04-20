import logging
import socket
import json
import argparse
from json import JSONDecodeError
from time import sleep
from random import randrange

logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(message)s')

def parse():
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', dest='host', type=str, default='localhost',
                        help="defines server host. [default host: localhost]")
    parser.add_argument('--port', dest='port', type=int, default=21000,
                        help="defines server port number [default port: 21000]")
    return parser.parse_args()

class PlayBot:
    def __init__(self, host, port):
        self.names = ['Mark', 'John', 'Alpha', 'Beta', 'Kappa',
                 'Mk. II', 'HAL 9000', 'Multivac', 'Prime',
                 'Legion', 'Cylons', 'A.L.I.E', 'Terminator']
        self.moves = ['NOP()', 'PATCH()', 'SCAN()', 'OVERLOAD()', 'OVERHEAR()', 'EXPLOIT()', 'INFECT()']
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.game = True
        self.heartbeat = 0
        self.run()

    def log(self, data):
        if type(data) == dict or type(data) == str:
            logging.info(data)
        else:
            logging.info(data.decode('utf-8'))

    def send(self, data):
        data += '\r\n'
        self.socket.sendall(data.encode('utf-8'))

    def connect(self):
        try:
            self.socket.connect((self.host, self.port))
            self.socket.settimeout(0.05)
        except OSError as e:
            self.log(f'Exception occurred when connecting to the server: {self.host}:{self.port}')
            self.log(e.strerror)
            self.game = False
        self.log('Connected Successfully...')

    def name(self):
        name = self.names[randrange(len(self.names))]
        self.send(name)
        self.log(f'Logged in as: {name}.')

    def login(self):
        if not self.game:
            return
        sleep(0.2)
        self.send('takeover')
        sleep(0.2)
        data = self.socket.recv(1000)
        if b'Name?' in data:
            self.name()
        else:
            self.game = False

    def heartbeat_socket(self):
        if self.heartbeat > 1500:
            self.send('ack')
            self.heartbeat = 0
        else:
            self.heartbeat += 1

    def get_data(self):
        try:
            self.heartbeat_socket()
            data = self.socket.recv(1024)
            return data
        except socket.timeout as e:
            return b''
        except ConnectionResetError as e:
            self.log(e.strerror)
            self.game = False
            return b''
        except ConnectionAbortedError as e:
            self.log(e.strerror)
            self.game = False
            return b''

    def move(self):
        move = self.moves[randrange(1, len(self.moves))]
        self.send(move)

    def move_ack(self, data):
        self.log('Move ACK.')

    def round_ends(self, data):
        self.heartbeat = 0
        try:
            data = json.loads(data)
            self.log(data['BOT_1'])
        except JSONDecodeError as e:
            self.log(f'Exception: {e.msg} while parsing data.')

    def game_ends(self, data):
        self.game = False
        self.log(data)

    def play(self):
        while self.game:
            data = self.get_data()

            if b'Command>' in data:  # Phase 1
                self.move()

            elif data.startswith(b'Command: '):  # Phase 2
                self.move_ack(data)

            elif data.startswith(b'{"TIME": '):  # Phase 3
                self.round_ends(data)

            elif data.startswith(b'{"WINNER":'):  # After Skirmish
                self.game_ends(data)

    def run(self):
        self.connect()
        self.login()
        self.play()


if __name__ == '__main__':
    args = parse()
    bot = PlayBot(host=args.host, port=args.port)
