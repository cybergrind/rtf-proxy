import asyncio
import json
import math
import struct
from collections import defaultdict

pos = [0, 0]
mypos = [0, 0]
samples = 0
stats = defaultdict(int)
counter = 0
enemies = {}


def format_packet(packet):
    _type = struct.unpack('!B', packet[:1])
    stats[_type[0]] += 1
    return f'Type: {_type} Payload: {packet}'


def print_unpack(format, packet):
    out = struct.unpack(format, packet)
    print('\t'.join(map(lambda x: str(x).rjust(8), out)).strip())


def dist(tx, ty):
    x, y = mypos
    return math.sqrt((tx - x) ** 2 + (ty - y) ** 2)


def get_angle(tx, ty):
    x, y = mypos
    return math.atan2(ty - y, tx - x)


def get_enemy():
    out = list(enemies.values())
    if out:
        out.sort(key=lambda x: x['dist'])
        return out[0]


def save_packet(packet):
    global counter
    counter += 1
    _type = struct.unpack('!B', packet[:1])[0]
    with open(f'packets/sample_{_type}_{counter:04d}.bin', 'wb') as f:
        f.write(packet)


async def out_loop(log, reader, writer):
    global mypos
    while True:
        skip = False
        size = await reader.read(4)
        if len(size) == 0:
            return
        if writer.is_closing():
            return
        _size_bytes = struct.unpack('!I', size)[0] - 4
        # print(f'Out Got size: {size} => {_size_bytes}')
        payload = await reader.read(_size_bytes)
        _type = struct.unpack('!B', payload[:1])[0]
        # 51 - position
        # 82 - shot
        if _type == 82 and _size_bytes == 24:
            # print_unpack('!BIHBIIfI', payload)
            o = list(struct.unpack('!BIHBIIfI', payload))
            x, y, angle = o[4], o[5], o[6]
            x, y = mypos
            print(f'Mypos: {x}\t\t{y}')
            # tx, ty = pos
            enemy = get_enemy()
            if enemy:
                tx, ty = enemy['tx'], enemy['ty']
                new_angle = get_angle(tx, ty)
                print(f'Shot at: {enemy} Old angle: {angle} New angle: {new_angle}')
                o[6] = new_angle
                payload = struct.pack('!BIHBIIfI', *o)
            # tangle = math.atan2(ty - y, tx - x)
            # print(f'{tangle - angle} == Tangle: {tangle} Vs {angle} / {tx}:{ty} | {x}:{y}')
            # modify = list(struct.unpack('!BIHBIIfI', payload))
            # if modify[3] == 145:
            #     print('modify: 145 => 155')
            #     modify[3] = 155
            # payload = struct.pack('!BIHBIIfI', *modify)
            pass
        elif _type == 51 and _size_bytes == 17:
            # print(format_packet(payload))
            # print_unpack('!BIIII', payload)
            out = struct.unpack('!BIIII', payload)
            mypos = [out[3], out[4]]
            pass
        log.write(f'Outgoing [{counter}]: Size: {_size_bytes} Payload: {format_packet(payload)}\n\n')
        if not skip:
            writer.write(size)
            writer.write(payload)
        else:
            print('Skip packet...')

        if writer.is_closing():
            return


def unp85(packet):
    # 14 each
    # b'U\x00\x00\x02\x9e\x00\x00\x00d\x00\x04\x00\x00\x07\xafBK\xdc5B\xed\x00\x00\x00\x00\x00\x00\x040BM]jB\xe3\xe9\x18\x00\x00\x00\x00\x03\xd2BG\xb0\xf0B\xdfT\x97\x00\x00\x00\x00\x03fBC\xe9\xc3B\xe1\xfa\xaf\x00\x00'
    global pos
    _type, _id, _num = struct.unpack('!BQH', packet[:11])
    # print(f'Num: {_num}')
    start = 11
    for i in range(_num):
        # start = 11 + 14 * i
        end = start + 14
        sub = packet[start:end]
        print(f'Len: {len(sub)} {start}/{end} => {sub}')
        sub = struct.unpack('!IIIH', sub)
        start = end
        print(f'Sub[{i}] => {sub}')
        if sub[3] > 0:
            end = start + sub[3]
            buff = packet[start:end]
            print(f'Buff: {buff} / {start}:{end} = {len(buff)}')
            start = end
        # 292 - ufo
        # 624 -?
        # if 300 < sub[1] < 38:
        #    pos = [sub[2], sub[3]]
    print(f'End: {end} VS {len(packet)}')


async def delete_enemy(_id):
    await asyncio.sleep(60)
    del enemies[_id]


def unp75(packet):
    _type, _num = struct.unpack('!BH', packet[:3])
    for i in range(_num):
        # size: 25
        start = 3 + i * 25
        end = 3 + i * 25 + 25
        print_unpack('!BIIIIII', packet[start:end])
        _i, _id, _a, _b, _c, _x, _y = struct.unpack('!BIIIIII', packet[start:end])
        if _id not in enemies:
            enemies[_id] = {'tx': _x, 'ty': _y}
            asyncio.create_task(delete_enemy(_id))
        enemies[_id]['dist'] = dist(_x, _y)


async def in_loop(log, reader, writer):
    while True:
        skip = False
        size = await reader.read(4)
        if len(size) == 0:
            return

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
        # 79 - map update
        # 85 - object move?
        if _type not in (21, 22, 26, 23, 78, 79, 83, 85, 87, 93, 155):
            print(format_packet(payload[:100]))

        if _type == 85:
            global samples
            # samples += 1
            # if samples < 100000000:
            #     with open(f'packets/sample_{samples}_85.bin', 'wb') as f:
            #         f.write(payload)
            # unp85(payload)
        elif _type == 27:
            print(format_packet(payload))
            # skip = True
        elif _type == 75:
            # skip = True
            # unp75(payload)
            # save_packet(payload)
            pass
        # print(f'Got payload: {payload}')
        log.write(
            f'Incoming [{counter}]: Size: {_size_bytes}/{len(payload)}/{size} Payload: {format_packet(payload)}\n\n'
        )
        if not skip:
            writer.write(size)
            writer.write(payload)
        else:
            print('Skip package')
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
        global stats
        log.write(json.dumps(stats, indent=4, sort_keys=True))
        stats = defaultdict(int)
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
