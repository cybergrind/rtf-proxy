import sys
import traceback
import asyncio
import json
import math
import struct

from rtf_proxy.bullet_analysis import (
    bullet_double,
    outcoming_shot,
    process_aoe_dmg,
    process_aoe_shot,
    process_bullet,
    process_hit_ack,
)
from rtf_proxy.obj_analysis import analyze_objects, artificial_status

from rtf_proxy.const import SAFE_LOCATIONS
from rtf_proxy.packet_tools import encode_packet, format_packet, print_unpack, save_packet
from rtf_proxy.state import new_state

VAULT_PACKET = b'\x01\x00\x05Vault\x00\x00\x00\x00\x00\x00\x08\x02\x00\x00ai'

out_writer = None
SAVE_PACKETS = [None, 59]


def log_err(fun):
    async def _wrapped(*args, **kwargs):
        try:
            return await fun(*args, **kwargs)
        except Exception as e:
            print(f'E: {e}')
            traceback.print_exc()
            raise
    return _wrapped


def goto_vault(writer):
    print('goto vault')
    if writer.is_closing():
        return
    writer.close()


@log_err
async def out_loop(state, reader, writer):
    global mypos
    # asyncio.create_task(deferred_vault(writer))
    while True:
        skip = False
        after = []
        size = await reader.readexactly(4)
        if len(size) == 0:
            print('size 0')
            return
        if writer.is_closing():
            print('wclosing')
            return
        if state.kill and not writer.is_closing():
            writer.close()

        while state.to_send:
            msg = state.to_send.pop()
            print(f'Send extra msg: {msg}')
            writer.write(msg)

        _size_bytes = struct.unpack('!I', size)[0] - 4
        # print(f'Out Got size: {size} => {_size_bytes}')
        payload = await reader.readexactly(_size_bytes)
        _type = struct.unpack('!B', payload[:1])[0]
        # 08 - aoe ack?
        # 27 - shot ack?
        # 35 - shot ack
        # 51 - position
        # 76 - bullet hit
        # 82 - shot
        # 84 - outcoming messages
        # 89 - shot landed in something else / wall
        # 98 - damaged by terrain?
        # 156 - set runes
        # 49 - use
        # 59 - move to inventory
        # 102 - drop
        # Out: Type: (49,) Payload: b'1\x00$$\x13\x00\x04\xaa8\x00\x00\x00S?\x00\x00\x00\x00\x00\x00\x00\x00\x01'
        # Ptype: 85 => {'mp': 1, 'status': 0, '0x60': 0}
        # Out: Type: (49,) Payload: b'1\x00$C\x06\x00\x04\xaa8\x00\x00\x00\n \x00\x00\x00\x00\x00\x00\x00\x00\x01'
        # Unpack + Use
        # Out: Type: (49,) Payload: b'1\x00+d\xe7\x00\x04a\x8c\x00\x00\x00S?\x00\x00\x00\x00\x00\x00\x00\x00\x01'
        # Out: Type: (49,) Payload: b'1\x00+k\xcd\x00\x04a\x8c\x00\x00\x00\n4\x00\x00\x00\x00\x00\x00\x00\x00\x01'

        if _type not in (3, 27, 30, 31, 35, 51, 76, 82, 84, 80, 89, 154):
            print(f'Out: {format_packet(payload[:100])}')

        if _type in SAVE_PACKETS: # (49, 59, 102, 51)
            save_packet(state, payload)
            # print(format_packet(payload))

        # if b'\x00\x00\x03\xdb' in payload:
        #     print(f'Health in out: {format_packet(payload)}')

        if _type == 82:
            payload = outcoming_shot(state, payload)

        if _type in (35,):
            process_hit_ack(state, payload)
            skip = True
        if _type == 84:
            skip = state.handle_cmd(payload)
        elif _type == 8:
            # AOE ack
            process_aoe_dmg(state, payload)
            skip = True
        elif _type == 98:
            # damaged by lava
            process_aoe_dmg(state, payload)
            skip = True
        elif _type == 76:
            # skip = True
            # payload = bullet_double(payload)
            if not payload:
                skip = True
        elif _type == 51:
            # print(format_packet(payload))
            # print_unpack('!BIIII', payload)
            out = list(struct.unpack('!BIIff', payload))
            packet_id = out[1]
            ts = out[2]
            state.set_mypos(out[3], out[4])
            new = state.set_ts(packet_id, ts)
            if new:
                out[2] = new
                print('Repack...')
                payload = struct.pack('!BIIff', *out)
            if state.scheduled:
                print(f'Packet: {packet_id} Scheduled: {state.scheduled}')
            if packet_id in state.scheduled:
                after = state.scheduled.pop(packet_id)

            for scheduled in after:
                state.log_write('Run scheduled...', stdout=True)
                scheduled()

        state.count_packet(payload)
        state.log_write(
            f'Outgoing [{state.counter}]: Size: {_size_bytes} [{size}] Payload: {format_packet(payload)}\n\n'
        )
        if not skip:
            if state.kill and not writer.is_closing():
                writer.close()
                print('out => return close')
                return
            writer.write(size)
            writer.write(payload)
        else:
            print(f'OUT Skip packet... {_type}')


@log_err
async def in_loop(state, reader, writer):
    # asyncio.create_task(artificial_status(state, writer))
    while True:
        skip = False
        size = await reader.readexactly(4)
        if len(size) == 0:
            print('isize 0')
            continue

        if writer.is_closing():
            return
        if state.kill and not writer.is_closing():
            writer.close()

        _size_bytes = struct.unpack('!I', size)[0] - 4
        # print(f'In Got size: {size} => {_size_bytes}')
        payload = await reader.readexactly(_size_bytes)
        while len(payload) < _size_bytes:
            remain = _size_bytes - len(payload)
            # print(f'Waiting for more: {remain} => {payload}')
            payload += await reader.read(remain)
        _type = struct.unpack('!B', payload[:1])[0]
        # 23 - message
        # 36 - terrain damage notify?
        # 40 - AOE?
        # 75 - enemy shots?
        # 79 - map update
        # 85 - object move?
        # 91 - death note
        # 98 ???
        # 159 - change realm?
        if _type not in (9, 21, 22, 26, 23, 27, 36, 75, 78, 79, 82, 83, 85, 87, 93, 155):
            print(f'In: {format_packet(payload[:100])}')

        if _type in (1,):
            state.enemies = {}
            _id, _size = struct.unpack('!BH', payload[:3])
            state.update_location(payload[3:3 + _size])
        elif _type == 159:
            state.on_teleport(payload)

        if _type in SAVE_PACKETS:
            save_packet(state, payload)

        # if b'\x00\x00\x03\xdb' in payload:
        #     print(f'Health in in: {format_packet(payload)}')
        # if _type == 79:
        #     if state.location == b'Vault' and not hasattr(state, 'hack'):
        #         skip = True
        #         state.hack = True

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
        elif _type == 40:
            # AOE shot
            process_aoe_shot(state, payload)
        elif _type == 36:
            process_aoe_dmg(state, payload)
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
        if not state.hp_safe:
            state.close()
        # print(f'Got payload: {payload}')
        state.count_packet(payload)
        state.log_write(
            f'Incoming [{state.counter}]: Size: {_size_bytes}/{len(payload)}/{size} '
            f'Payload: {format_packet(payload)}\n\n'
        )
        if not skip:
            if state.kill and not writer.is_closing():
                writer.close()
                print('in return close')
                return
            writer.write(size)
            writer.write(payload)
        else:
            print(f'IN Skip packet {_type}')


async def handle_incoming(local_reader, local_writer):
    print('Handle incoming. Connecting to remote ...')
    remote_reader, remote_writer = await asyncio.open_connection('192.223.31.195', 2051)
    print('Connected. Run')
    state = new_state()
    global out_writer
    out_writer = remote_writer
    state.remote_writer = remote_writer
    state.local_writer = local_writer
    try:
        ret = await asyncio.wait(
            [
                out_loop(state, local_reader, remote_writer),
                in_loop(state, remote_reader, local_writer),
            ],
            return_when=asyncio.FIRST_EXCEPTION,
        )
        print(f'Ret: {ret}')
    except Exception as e:
        print(f'Got Exc: {e}')
    finally:
        print('Close all')
        state.close()
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
