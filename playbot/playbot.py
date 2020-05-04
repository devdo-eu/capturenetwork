import logging
import socket
import argparse
from json import JSONDecodeError, loads
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
        self.my_move = ''
        self.move_ok = False
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.game = False
        self.heartbeat = 0
        self.run()

    def log(self, data):
        if type(data) == dict or type(data) == str:
            logging.info(data)
        else:
            logging.info(data.decode())

    def send(self, data):
        self.socket.sendall(f'{data}\x04'.encode())

    def connect(self):
        try:
            self.socket.connect((self.host, self.port))
            self.socket.setblocking(False)
            self.log('Connected Successfully...')
        except OSError as e:
            self.log(f'Exception occurred when connecting to the server: {self.host}:{self.port}')
            self.log(e.strerror)
            self.log('End of workout...')

    def name(self):
        name = self.names[randrange(len(self.names))]
        self.send(name)
        self.log(f'Logged in as: {name}.')

    def login(self):
        sleep(0.1)
        self.send('takeover')
        sleep(0.1)
        data = self.get_data()
        if 'Name?' in data:
            self.name()
            self.game = True

    def heartbeat_socket(self):
        if self.heartbeat > 15000:
            self.send('ack')
            self.heartbeat = 0
        else:
            self.heartbeat += 1

    def get_data(self):
        buffor = ''
        try:
            while True:
                self.heartbeat_socket()
                buffor += self.socket.recv(1).decode()
                if '\x04' in buffor:
                    self.heartbeat = 0
                    return buffor.split('\x04')[0]
        except BlockingIOError:
            return buffor
        except ConnectionResetError as e:
            buffor = e.strerror
        except ConnectionAbortedError as e:
            buffor = e.strerror

        self.log(buffor)
        self.game = False
        return ''

    def move(self):
        self.my_move = self.moves[randrange(1, len(self.moves))]
        self.send(self.my_move)

    def move_ack(self, data):
        if self.my_move in data:
            self.log('Move ACK.')
            self.move_ok = True
        else:
            self.send(self.my_move)

    def round_ends(self, data):
        try:
            self.move_ok = False
            data = loads(data)
            self.log(data['BOT_1'])
        except JSONDecodeError as e:
            self.log(f'Exception: {e.msg} while parsing data.')

    def game_ends(self, data):
        self.game = False
        self.log(data)

    def play(self):
        while self.game:
            data = self.get_data()
            if data == '':
                sleep(0.01)

            if 'Command>' in data:  # Phase 1
                self.move()

            elif data.startswith('Command: ') and not self.move_ok:  # Phase 2
                self.move_ack(data)

            elif data.startswith('{"TIME": '):  # Phase 3
                self.round_ends(data)

            elif data.startswith('{"WINNER":'):  # After Skirmish
                self.game_ends(data)

    def run(self):
        self.connect()
        self.login()
        self.play()


if __name__ == '__main__':
    args = parse()
    bot = PlayBot(host=args.host, port=args.port)
