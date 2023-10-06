import argparse
import typing
import socket
import asyncio
import logging

from config import KEY, SERVER_ADDR, SERVER_PORT, LOCAL_PORT, LOCAL_ADDR, CHACHA20_NONCE, CFB_IV, OFB_NONCE, \
    CTR_NONCE
from utils import net
from core.cipher import Cipher, CipherFactory
from core.securesocket import SecureSocket

Connection = socket.socket
logger = logging.getLogger(__name__)


class LsLocal(SecureSocket):
    def __init__(self,
                 loop: asyncio.AbstractEventLoop,
                 listenAddr: net.Address,
                 remoteAddr: net.Address,
                 cipher_type: str) -> None:
        if cipher_type == "ChaCha20":
            cipher = CipherFactory.create_cipher("ChaCha20", KEY, CHACHA20_NONCE)
        elif cipher_type == "AES-256-CFB":
            cipher = CipherFactory.create_cipher("AES-256-CFB", KEY, CFB_IV)
        elif cipher_type == "AES-256-OFB":
            cipher = CipherFactory.create_cipher("AES-256-OFB", KEY, OFB_NONCE)
        elif cipher_type == "AES-256-CTR":
            cipher = CipherFactory.create_cipher("AES-256-CTR", KEY, CTR_NONCE)
        else:
            raise ValueError("Invalid cipher type")

        super().__init__(loop=loop, cipher=cipher)
        self.listenAddr = listenAddr
        self.remoteAddr = remoteAddr

    async def listen(self, didListen: typing.Callable=None):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as listener:
            listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            listener.bind(self.listenAddr)
            listener.listen(socket.SOMAXCONN)
            listener.setblocking(False)

            logger.info('Listen to %s:%d' % self.listenAddr)
            if didListen:
                didListen(listener.getsockname())

            while True:
                connection, address = await self.loop.sock_accept(listener)
                logger.info('Receive %s:%d', *address)
                asyncio.ensure_future(self.handleConn(connection))

    async def handleConn(self, connection: Connection):
        remoteServer = await self.dialRemote()

        def cleanUp(task):
            """
            Close the socket when they succeeded or had an exception.
            """
            remoteServer.close()
            connection.close()

        local2remote = asyncio.ensure_future(
            self.decodeCopy(connection, remoteServer))
        remote2local = asyncio.ensure_future(
            self.encodeCopy(remoteServer, connection))
        task = asyncio.ensure_future(
            asyncio.gather(
                local2remote,
                remote2local,
                loop=self.loop,
                return_exceptions=True))
        task.add_done_callback(cleanUp)

    async def dialRemote(self):
        """
        Create a socket that connects to the Remote Server.
        """
        try:
            remoteConn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            remoteConn.setblocking(False)
            await self.loop.sock_connect(remoteConn, self.remoteAddr)
        except Exception as err:
            raise ConnectionError('Connect to remote server %s:%d failed:\n%r' % (*self.remoteAddr,err))
        return remoteConn



if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        usage='%(prog)s local_ip local_port server_ip server_port [--cipher-type {ChaCha20,AES-256-CFB,AES-256-OFB,AES-256-CTR}]',
        description='LS Client - Secure file transfer client'
    )

    parser.add_argument('local_ip', type=str, help='The local IP address')
    parser.add_argument('local_port', type=int, help='The local port number')
    parser.add_argument('server_ip', type=str, help='The server IP address')
    parser.add_argument('server_port', type=int, help='The server port number')
    parser.add_argument('--cipher-type', type=str, default='ChaCha20',
                        choices=['ChaCha20', 'AES-256-CFB', 'AES-256-OFB', 'AES-256-CTR'],
                        help='The encryption cipher type for secure communication')

    args = parser.parse_args()

    loop = asyncio.get_event_loop()
    localAddr = net.Address(args.local_ip, args.local_port)
    remoteAddr = net.Address(args.server_ip, args.server_port)
    print(f'LS client is starting on {localAddr} connecting to {remoteAddr} using {args.cipher_type} encryption')

    client = LsLocal(loop, localAddr, remoteAddr, args.cipher_type)

    loop.run_until_complete(client.listen())
    loop.run_forever()
