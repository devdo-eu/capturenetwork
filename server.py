import logging
import selectors
import socket

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


class SelectorServer:
    """
    Create the selector object that will dispatch events. Register
    interest in read events, that include incoming connections.
    The handler method is passed in data so we can fetch it in
    serve_forever.
    """
    def __init__(self, greetings, host, port):
        """
        Create the main socket that accepts incoming connections and start
        listening. The socket is blocking with timeout set to 5ms.
        :param greetings: Message which will be send to client on connection
        :param host: Address on which server will be available
        :param port: Port number for connection
        """
        self.__main_socket = socket.socket()
        self.__main_socket.bind((host, port))
        self.__main_socket.listen(100)
        self.__main_socket.settimeout(0.005)
        self.__greetings = greetings
        self.__selector = selectors.DefaultSelector()
        self.__selector.register(fileobj=self.__main_socket,
                                 events=selectors.EVENT_READ,
                                 data=self.onAccept)
        self.__current_peers = {}
        self.__current_number_of_peers = 0
        self.__peerData = {}

        self.closed = False
        self.conns = []

    def close(self):
        """
        Method used to close SelectorServer main_socket
        """
        for conn in self.conns:
            self.closeConnection(conn)
        self.__main_socket.close()
        self.closed = True
        logging.info('all connection closed & cleaned up\r\n')

    def sendToConn(self, peername, message):
        """
        Method used to send messages to peers
        :param peername: Object used to identify receiver of message
        :param message: Message to send
        """
        for conn in self.conns:
            if conn.getpeername() == peername:
                conn.send(message)

    def onAccept(self, sock):
        """
        This is a handler for the main_socket which is now listening, so we
        know it's ready to accept a new connection.
        Register interest in read events on the new socket, dispatching to
        self.onRead
        :param sock: All socket data
        """
        conn, addr = self.__main_socket.accept()
        conn = Connection(conn)
        logging.info('accepted connection from {0}'.format(addr))
        conn.get().setblocking(False)
        conn.send(self.__greetings)

        self.__current_peers[conn.get().fileno()] = conn.getpeername()
        self.conns.append(conn)
        self.__selector.register(fileobj=conn.get(), events=selectors.EVENT_READ,
                                 data=self.onRead)

    def closeConnection(self, conn):
        """
        Can't ask conn for getpeername() here, because the peer may no
        longer exist (hung up). Instead we use our own mapping of socket
        fds to peer names - our socket fd is still open.
        :param conn: Connection object to close
        """
        if self.__current_peers.get(conn.get().fileno(), 'NA') == 'NA':
            return
        peername = self.__current_peers[conn.get().fileno()]
        logging.info('closing connection to {0}'.format(peername))
        try:
            del self.__current_peers[conn.get().fileno()]
            self.__selector.unregister(conn.get())
        except KeyError:
            logging.info('no peer...')
        conn.get().close()
        self.__current_number_of_peers -= 1
        logging.info('Num active peers = {0}'.format(
            len(self.__current_peers)))

    def onRead(self, conn):
        """
        Method used to handle event
        when there is data to read inside protocol buffer
        :param conn: Object with connection
        """
        conn = Connection(conn)
        try:
            data = conn.recv()
            if data:
                peername = conn.getpeername()
                self.__peerData[peername] = data
        except (ConnectionResetError, OSError) as e:
            logging.info(f'Exception: {e.strerror}')
            self.closeConnection(conn)

    def getData(self):
        return self.__peerData

    def serveForever(self):
        """
        Main method of SelectorServer.
        It is responsible for collecting connections from peers.
        """
        while True:
            events = self.__selector.select(timeout=0.2)

            for key, _ in events:
                handler = key.data
                handler(key.fileobj)

            if self.__current_number_of_peers < len(self.__current_peers):
                self.__current_number_of_peers = len(self.__current_peers)
                logging.info('Running report...')
                logging.info('Num active peers = {0}'.format(
                    len(self.__current_peers)))
