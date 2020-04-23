import logging
import selectors
import socket

logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(message)s')


class SelectorServer:
    def __init__(self, greetings, host, port):
        # Create the main socket that accepts incoming connections and start
        # listening. The socket is nonblocking.
        self.main_socket = socket.socket()
        self.main_socket.bind((host, port))
        self.main_socket.listen(100)
        self.main_socket.settimeout(0.05)
        # self.main_socket.setblocking(False)
        self.greetings = greetings
        self.closed = False

        # Create the selector object that will dispatch events. Register
        # interest in read events, that include incoming connections.
        # The handler method is passed in data so we can fetch it in
        # serve_forever.
        self.selector = selectors.DefaultSelector()
        self.selector.register(fileobj=self.main_socket,
                               events=selectors.EVENT_READ,
                               data=self.on_accept)

        # Keeps track of the peers currently connected. Maps socket fd to
        # peer name.
        self.current_peers = {}
        self.conns = []
        self.current_number_of_peers = 0
        self.__peerData = {}

    def close(self):
        for conn in self.conns:
            self.close_connection(conn)
        self.main_socket.close()
        self.closed = True
        logging.info('all connection closed & cleaned up\r\n')

    def send_to_conn(self, peername, message):
        for conn in self.conns:
            if conn.getpeername() == peername:
                conn.send(message.encode('utf-8'))

    def on_accept(self, sock, mask):
        # This is a handler for the main_socket which is now listening, so we
        # know it's ready to accept a new connection.
        conn, addr = self.main_socket.accept()
        logging.info('accepted connection from {0}'.format(addr))
        conn.setblocking(False)
        conn.send(self.greetings.encode('utf-8'))

        self.current_peers[conn.fileno()] = conn.getpeername()
        self.conns.append(conn)
        # Register interest in read events on the new socket, dispatching to
        # self.on_read
        self.selector.register(fileobj=conn, events=selectors.EVENT_READ,
                               data=self.on_read)

    def close_connection(self, conn):
        # We can't ask conn for getpeername() here, because the peer may no
        # longer exist (hung up); instead we use our own mapping of socket
        # fds to peer names - our socket fd is still open.
        if self.current_peers.get(conn.fileno(), 'NA') == 'NA':
            return
        peername = self.current_peers[conn.fileno()]
        logging.info('closing connection to {0}'.format(peername))
        del self.current_peers[conn.fileno()]
        self.selector.unregister(conn)
        conn.close()
        self.current_number_of_peers -= 1
        logging.info('Num active peers = {0}'.format(
            len(self.current_peers)))

    def on_read(self, conn, mask):
        try:
            data = conn.recv(1000)
            if data:
                peername = conn.getpeername()
                logging.info('got data from {}: {!r}'.format(peername, data))
                self.__peerData[peername] = data.decode('utf-8')
        except ConnectionResetError as e:
            logging.info(f'ConnectionResetErrorException: {e.strerror}')
            self.close_connection(conn)
        except OSError as e:
            logging.info(f'OSError Exception: {e.strerror}')
            self.close_connection(conn)

    def get_data(self):
        return self.__peerData

    def serve_forever(self):
        while True:
            events = self.selector.select(timeout=0.2)

            # For each new event, dispatch to its handler
            for key, mask in events:
                handler = key.data
                handler(key.fileobj, mask)

            if self.current_number_of_peers < len(self.current_peers):
                self.current_number_of_peers = len(self.current_peers)
                logging.info('Running report...')
                logging.info('Num active peers = {0}'.format(
                    len(self.current_peers)))
