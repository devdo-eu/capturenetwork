import logging
import socket
import argparse
from mind import Mind
from time import sleep, time

logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(message)s')


def log(data):
    if type(data) == dict or type(data) == str:
        logging.info(data)
    else:
        logging.info(data.decode())


def parse():
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', dest='host', type=str, default='localhost',
                        help="defines server host. [default host: localhost]")
    parser.add_argument('--port', dest='port', type=int, default=21000,
                        help="defines server port number [default port: 21000]")
    return parser.parse_args()


class PlayBot:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.heartbeat = 0
        self.game = False
        self.mind = Mind(log)
        self.run()

    def send(self, data):
        self.socket.sendall(f'{data}\x04'.encode())

    def connect(self):
        try:
            self.socket.connect((self.host, self.port))
            self.socket.setblocking(False)
            log('Connected Successfully...')
        except OSError as e:
            log(f'Exception occurred when connecting to the server: {self.host}:{self.port}')
            log(e.strerror)
            log('End of workout...')

    def login(self):
        deadline = time() + 5
        data = ''
        while data == '' and time() < deadline:
            data = self.get_data()
            sleep(0.1)
        if '<<<Battle.Server>>>' not in data:
            raise Exception('Wrong server. End of workout...')

        sleep(0.1)
        self.send('takeover')
        sleep(0.1)
        data = ''
        while data == '' and time() < deadline:
            data = self.get_data()
            sleep(0.1)
        if 'Name?' in data:
            self.send(self.mind.name())
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
            self.game = True
        except (ConnectionResetError, ConnectionAbortedError) as e:
            buffor = ''
            log(e.strerror)
            self.game = False
        return buffor

    def move_ack(self, data):
        ack = self.mind.move_ack(data)
        if ack != '':
            self.send(ack)

    def play(self):
        while self.game:
            data = self.get_data()
            if data == '':
                sleep(0.001)

            if 'Command>' in data:  # Phase 1
                self.send(self.mind.move())

            elif data.startswith('Command: '):  # Phase 2
                self.move_ack(data)

            elif data.startswith('{"TIME": '):  # Phase 3
                self.mind.round_ends(data)

            elif data.startswith('{"WINNER":'):  # After Skirmish
                self.mind.game_ends(data)
                self.game = False

    def run(self):
        self.connect()
        self.login()
        self.play()


if __name__ == '__main__':
    args = parse()
    bot = PlayBot(host=args.host, port=args.port)
