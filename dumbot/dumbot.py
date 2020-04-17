import logging
import socket
import json
from json import JSONDecodeError
from time import sleep
from random import randrange

logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(message)s')

HOST = 'localhost'  # The server's hostname or IP address
PORT = 21000        # The port used by the server

names = ['Mark', 'John', 'Alpha', 'Beta', 'Kappa',
         'Mk. II', 'HAL 9000', 'Multivac', 'Prime',
         'Legion', 'Cylons', 'A.L.I.E', 'Terminator']
names_len = len(names)

moves = ['NOP()', 'PATCH()', 'SCAN()', 'OVERLOAD()', 'OVERHEAR()', 'EXPLOIT()', 'INFECT()']
moves_len = len(moves)

history = []

def log(data):
    if type(data) == dict or type(data) == str:
        logging.info(data)
    else:
        logging.info(data.decode('utf-8'))


def send(data):
    data += '\r\n'
    s.sendall(data.encode('utf-8'))
    data = ('>> ' + data).encode('utf-8')
    log(data)


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    game = True
    try:
        sleep(1)
        data = s.recv(1000)
        log(data)
        send('takeover')
        sleep(0.01)
        data = s.recv(1000)
        if data == b'Name?\r\n':
            log(data)
            name = names[randrange(len(names))]
            send(name)
        while game:
            try:
                sleep(0.01)
                data = s.recv(1000)
                if data == b'Command>\r\n':
                    log(data)
                    move = moves[randrange(1, moves_len)]
                    send(move)
                elif data.startswith(b'Command: '):
                    log(data)
                elif data.startswith(b'{"TIME": '):
                    # log(data)
                    try:
                        data = json.loads(data)
                        history.append(data)
                        log(data['BOT_1'])
                    except JSONDecodeError as e:
                        log(f'Exception: {e.msg} while parsing data.')

                else:
                    log(data)
                    game = False
            except KeyboardInterrupt:
                game = False
                break
    except KeyboardInterrupt:
        logging.info('Interrupted! Closing...')