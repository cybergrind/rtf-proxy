import asyncio
import json
import math
import struct

from rtf_proxy.packet_tools import format_packet, print_unpack, save_packet, encode_packet
from rtf_proxy.state import new_state
from rtf_proxy.obj_analysis import analyze_objects, artificial_status
from rtf_proxy.bullet_analysis import process_bullet, outcoming_shot, bullet_double


VAULT_PACKET = b'\x01\x00\x05Vault\x00\x00\x00\x00\x00\x00\x08\x02\x00\x00ai'
SAFE_LOCATIONS = [b'Nexus', b'Market', b'Vault']

out_writer = None


def goto_vault(writer):
    print('goto vault')
    if writer.is_closing():
        return
    writer.close()


async def out_loop(state, reader, writer):
    global mypos
    # asyncio.create_task(deferred_vault(writer))
    while True:
        skip = False
        size = await reader.read(4)
        if len(size) == 0:
            return
        if writer.is_closing():
            return
        if state.kill and not writer.is_closing():
            writer.close()
        _size_bytes = struct.unpack('!I', size)[0] - 4
        # print(f'Out Got size: {size} => {_size_bytes}')
        payload = await reader.read(_size_bytes)
        _type = struct.unpack('!B', payload[:1])[0]
        # 27 - shot ack?
        # 35 - shot landed ack?
        # 51 - position
        # 76 - bullet is landed
        # 82 - shot
        # 89 - shot landed in something else / wall
        # 156 - set runes
        if _type not in (3, 27, 30, 51, 82, 84, 154):
            print(f'Out: {format_packet(payload[:100])}')
        if _type in (35, 89):
            save_packet(state, payload)
            # print(format_packet(payload))

        # if b'\x00\x00\x03\xdb' in payload:
        #     print(f'Health in out: {format_packet(payload)}')

        if _type == 82:
            payload = outcoming_shot(state, payload)
            # print_unpack('!BIHBIIfI', payload)
            # o = list(struct.unpack('!BIHBIIfI', payload))
            # x, y, angle = o[4], o[5], o[6]
            # x, y = mypos
            # print(f'Mypos: {x}\t\t{y}')
            # tx, ty = pos
            # enemy = get_enemy()
            # if enemy:
            #     tx, ty = enemy['tx'], enemy['ty']
            #     new_angle = get_angle(tx, ty)
            #     print(f'Shot at: {enemy} Old angle: {angle} New angle: {new_angle}')
            #     o[6] = new_angle
            #     payload = struct.pack('!BIHBIIfI', *o)
            # tangle = math.atan2(ty - y, tx - x)
            # print(f'{tangle - angle} == Tangle: {tangle} Vs {angle} / {tx}:{ty} | {x}:{y}')
            # modify = list(struct.unpack('!BIHBIIfI', payload))
            # if modify[3] == 145:
            #     print('modify: 145 => 155')
            #     modify[3] = 155
            # payload = struct.pack('!BIHBIIfI', *modify)
            pass
        elif _type in (35,):
            skip = True
        elif _type == 76:
            # skip = True
            # payload = bullet_double(payload)
            if not payload:
                skip = True
        elif _type == 51 and _size_bytes == 17:
            # print(format_packet(payload))
            # print_unpack('!BIIII', payload)
            out = struct.unpack('!BIIII', payload)
            state.set_mypos(out[3], out[4])
            pass
        state.count_packet(payload)
        state.log.write(f'Outgoing [{state.counter}]: Size: {_size_bytes} Payload: {format_packet(payload)}\n\n')
        if not skip:
            writer.write(size)
            writer.write(payload)
        else:
            print('Skip packet...')


async def in_loop(state, reader, writer):
    # asyncio.create_task(artificial_status(state, writer))
    while True:
        skip = False
        size = await reader.read(4)
        if len(size) == 0:
            return

        if writer.is_closing():
            return
        if state.kill and not writer.is_closing():
            writer.close()

        _size_bytes = struct.unpack('!I', size)[0] - 4
        # print(f'In Got size: {size} => {_size_bytes}')
        payload = await reader.read(_size_bytes)
        while len(payload) < _size_bytes:
            remain = _size_bytes - len(payload)
            # print(f'Waiting for more: {remain} => {payload}')
            payload += await reader.read(remain)
        _type = struct.unpack('!B', payload[:1])[0]
        # 23 - message
        # 35 - ping ack?
        # 40 - AOE?
        # 75 - enemy shots?
        # 79 - map update
        # 85 - object move?
        # 159 - change realm?
        if _type not in (9, 21, 22, 26, 23, 27, 75, 78, 79, 82, 83, 85, 87, 93, 155):
            print(f'In: {format_packet(payload[:100])}')

        if _type in (1,):
            state.enemies = {}
            if any([x in payload for x in SAFE_LOCATIONS]):
                state.safe = True
            else:
                state.safe = False
            print(f'Location to: {state.safe}')

        if _type in (None,):
            save_packet(state, payload)

        # if b'\x00\x00\x03\xdb' in payload:
        #     print(f'Health in in: {format_packet(payload)}')

        if _type == 85:
            global samples
            # samples += 1
            # if samples < 100000000:
            #     with open(f'packets/sample_{samples}_85.bin', 'wb') as f:
            #         f.write(payload)
            # unp85(payload)
        elif _type == 75:
            payload = process_bullet(state, payload)
            # skip = True
            # unp75(payload)
            # save_packet(state, payload)
            pass
        elif _type == 78:
            # save_packet(state, payload)
            pass
        elif _type == 79:
            # save_packet(state, payload)
            pass
        if _type in (79, 85):
            payload = analyze_objects(state, payload)
            if b'cybergrind' in payload:
                # print('REPLACE!!!!')
                # payload.replace(b'\x00\x08\x00\x00#g', b'\x00\x08\x00\x00#h')
                # payload.replace(b'\x06110601|\x00\x00\x00$', b'\x06110601|\x00\x00\x00\x88')
                pass
        if not state.safe and (state.hp_level < 0.5 and state.hp < 600):
            print(f'Critical level: {state.hp_level}')
            goto_vault()
        # print(f'Got payload: {payload}')
        state.count_packet(payload)
        state.log.write(
            f'Incoming [{state.counter}]: Size: {_size_bytes}/{len(payload)}/{size} '
            f'Payload: {format_packet(payload)}\n\n'
        )
        if not skip:
            writer.write(size)
            writer.write(payload)
        else:
            print('Skip package')


async def handle_incoming(local_reader, local_writer):
    print('Handle incoming. Connecting to remote ...')
    remote_reader, remote_writer = await asyncio.open_connection('192.223.31.195', 2051)
    print('Connected. Run')
    state = new_state()
    global out_writer
    out_writer = remote_writer
    try:
        ret = await asyncio.wait(
            [out_loop(state, local_reader, remote_writer), in_loop(state, remote_reader, local_writer)],
            return_when=asyncio.FIRST_EXCEPTION,
        )
        print(f'Ret: {ret}')
    except Exception as e:
        print(f'Got Exc: {e}')
    finally:
        state.close()
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
