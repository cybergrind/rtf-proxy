import struct
import asyncio


class ClientProtocol(asyncio.Protocol):
    def __init__(self, server, loop):
        self.server = server
        self.loop = loop
        self.closed = False

    def connection_made(self, transport):
        # transport.write(self.message.encode())
        self.transport = transport
        self.server.proxy_ok(self)

    def send(self, data):
        self.transport.write(data)

    def data_received(self, data):
        print('Data received: {!r}'.format(data))
        self.server.on_message(data)

    def connection_lost(self, exc):
        print('The server closed the connection')
        self.server.lost()

    def lost(self):
        if not self.closed:
            self.closed = True
            self.transport.close()


class ServerProtocol(asyncio.Protocol):
    def connection_made(self, transport):
        self.closed = False
        self.client = None
        self.buff = []
        self.loop = asyncio.get_event_loop()
        peername = transport.get_extra_info('peername')
        self.loop.create_task(self.loop.create_connection(lambda: ClientProtocol(self, self.loop), '192.223.31.195', 2051))
        print('Connection from {}'.format(peername))
        self.transport = transport
        self.log = open('messages.log', 'w')

    def proxy_ok(self, client):
        self.client = client
        for data in self.buff:
            self.client.send(data)
        self.buff = []

    def format(self, packet):
        _size, _type = struct.unpack('!Ih', packet[:6])
        return f'Size: {_size} Type: {_type} Payload: {packet}'

    def on_message(self, data):
        self.log.write(f'Recvd: {len(data)} => {self.format(data)}\n\n')
        self.transport.write(data)

    def data_received(self, data):
        print(f'Forward: {data}')
        self.log.write(f'Send: {len(data)} => {self.format(data)}\n\n')
        if self.client:
            self.client.send(data)
        else:
            self.buff.append(data)

    def lost(self):
        self.client = None
        if not self.closed:
            self.transport.close()
            self.closed = True

    def connection_lost(self, exc):
        self.log.close()
        self.closed = True
        if self.client:
            self.client.lost()

async def main():
    loop = asyncio.get_event_loop()
    # coro = asyncio.start_server(handle_data, '0.0.0.0', 9995, loop=loop)
    server = await loop.create_server(lambda: ServerProtocol(), '0.0.0.0', 9995)
    # server = loop.run_until_complete(coro)
    print(f'Run server: {server}', flush=True)
    async with server:
        await server.serve_forever()


if __name__ == '__main__':
    asyncio.run(main())
