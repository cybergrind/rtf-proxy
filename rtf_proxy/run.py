import asyncio
import struct


def format_packet(packet):
    _type = struct.unpack('!B', packet[:1])
    return f'Type: {_type} Payload: {packet}'


def print_unpack(format, packet):
    out = struct.unpack('!BIHHHHHHHHHB', packet)
    print(''.join(map(lambda x: str(x).rjust(8), out)).strip())


async def out_loop(log, reader, writer):
    while True:
        size = await reader.read(4)
        if len(size) == 0:
            return
        if writer.is_closing():
            return
        writer.write(size)
        _size_bytes = struct.unpack('!I', size)[0]
        # print(f'Out Got size: {size} => {_size_bytes}')
        payload = await reader.read(_size_bytes)
        _type = struct.unpack('!B', payload[:1])[0]
        if _type == 82:
            print_unpack('!BIHHHHHHHHHB', payload)
        log.write(f'Outgoing: Size: {_size_bytes} Payload: {format_packet(payload)}\n\n')
        writer.write(payload)
        if writer.is_closing():
            return


async def in_loop(log, reader, writer):
    while True:
        size = await reader.read(4)
        if len(size) == 0:
            return
        writer.write(size)
        if writer.is_closing():
            return
        _size_bytes = struct.unpack('!I', size)[0]
        # print(f'In Got size: {size} => {_size_bytes}')
        payload = await reader.read(_size_bytes)
        # print(f'Got payload: {payload}')
        log.write(f'Incoming: Size: {_size_bytes} Payload: {format_packet(payload)}\n\n')
        writer.write(payload)
        if writer.is_closing():
            return


async def handle_incoming(local_reader, local_writer):
    print('Handle incoming. Connecting to remote ...')
    remote_reader, remote_writer = await asyncio.open_connection('192.223.31.195', 2051)
    print('Connected. Run')
    log = open('messages.log', 'w')
    try:
        ret = await asyncio.wait(
            [out_loop(log, local_reader, remote_writer), in_loop(log, remote_reader, local_writer)],
            return_when=asyncio.FIRST_EXCEPTION,
        )
        print(f'Ret: {ret}')
    except Exception as e:
        print(f'Got Exc: {e}')
    finally:
        log.close()
        print('Close all')
        local_writer.close()
        remote_writer.close()


async def main():
    loop = asyncio.get_event_loop()
    server = await asyncio.start_server(handle_incoming, '0.0.0.0', 9995, loop=loop)
    # server = await loop.create_server(lambda: ServerProtocol(), '0.0.0.0', 9995)
    # server = loop.run_until_complete(coro)
    print(f'Run server: {server}', flush=True)
    async with server:
        await server.serve_forever()


if __name__ == '__main__':
    asyncio.run(main())
