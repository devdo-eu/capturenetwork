import logging

logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(message)s')


class Connection:
    """
    Helper class to manage and handle connection related operations
    """
    def __init__(self, conn):
        self.__EOT = '\n\x04\n'
        self.__conn = conn

    def get(self):
        return self.__conn

    def getpeername(self):
        return self.__conn.getpeername()

    def send(self, message):
        self.__conn.send(f'{message}{self.__EOT}'.encode())

    def recv(self):
        data = ''
        limit = 32000
        while True:
            limit -= 1
            data += self.__conn.recv(1).decode()
            if self.__EOT in data or limit == 0:
                data = data.split(self.__EOT)[0]
                break
        if data:
            logging.info(f'got data from {self.__conn.getpeername()}: {data}')
        return data
