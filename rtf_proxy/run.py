import asyncio
import struct


def format_packet(packet):
    _type = struct.unpack('!B', packet[:1])
    return f'Type: {_type} Payload: {packet}'


def print_unpack(format, packet):
    out = struct.unpack(format, packet)
    print('\t'.join(map(lambda x: str(x).rjust(8), out)).strip())


async def out_loop(log, reader, writer):
    while True:
        size = await reader.read(4)
        if len(size) == 0:
            return
        if writer.is_closing():
            return
        writer.write(size)
        _size_bytes = struct.unpack('!I', size)[0] - 4
        # print(f'Out Got size: {size} => {_size_bytes}')
        payload = await reader.read(_size_bytes)
        _type = struct.unpack('!B', payload[:1])[0]
        # 51 - position
        # 82 - shot
        if _type == 82 and _size_bytes == 24:
            print_unpack('!BIHBIIfI', payload)
            # modify = list(struct.unpack('!BIHBIIfI', payload))
            # if modify[3] == 145:
            #     print('modify: 145 => 155')
            #     modify[3] = 155
            # payload = struct.pack('!BIHBIIfI', *modify)
            pass
        if _type == 51 and _size_bytes == 17:
            # print(format_packet(payload))
            # print_unpack('!BIIII', payload)
            pass
        log.write(f'Outgoing: Size: {_size_bytes} Payload: {format_packet(payload)}\n\n')
        writer.write(payload)
        if writer.is_closing():
            return


def unp85(packet):
    # 14 each
    # b'U\x00\x00\x02\x9e\x00\x00\x00d\x00\x04\x00\x00\x07\xafBK\xdc5B\xed\x00\x00\x00\x00\x00\x00\x040BM]jB\xe3\xe9\x18\x00\x00\x00\x00\x03\xd2BG\xb0\xf0B\xdfT\x97\x00\x00\x00\x00\x03fBC\xe9\xc3B\xe1\xfa\xaf\x00\x00'
    _type, _id, _num = struct.unpack('!BQH', packet[:11])
    # print(f'Num: {_num}')
    for i in range(_num):
        start = 11 + 14 * i
        end = start + 14
        sub = packet[start:end]
        sub = struct.unpack('!HHIIBB', sub)
        print(f'Sub[{i}] => {sub}')

async def in_loop(log, reader, writer):
    while True:
        size = await reader.read(4)
        if len(size) == 0:
            return
        writer.write(size)
        if writer.is_closing():
            return
        _size_bytes = struct.unpack('!I', size)[0] - 4
        # print(f'In Got size: {size} => {_size_bytes}')
        payload = await reader.read(_size_bytes)
        while len(payload) < _size_bytes:
            remain = _size_bytes - len(payload)
            # print(f'Waiting for more: {remain} => {payload}')
            payload += await reader.read(remain)
        _type = struct.unpack('!B', payload[:1])[0]
        # 23 - message
        # 75 - enemy shots?
        # 79 - map
        # 85 - object move? H(type)I(id)I(numthen)
        if _type not in (21, 22, 26, 23, 78, 79, 83, 85, 87, 93, 155):
            print(format_packet(payload[:100]))
        elif _type == 85:
            unp85(payload)
        # print(f'Got payload: {payload}')
        log.write(f'Incoming: Size: {_size_bytes}/{len(payload)}/{size} Payload: {format_packet(payload)}\n\n')
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
