from binascii import hexlify
import struct


def format_packet(packet):
    _type = struct.unpack('!B', packet[:1])
    return f'Type: {_type} Payload: {packet}'


def print_unpack(state, format, packet):
    out = struct.unpack(format, packet)
    print('\t'.join(map(lambda x: str(x).rjust(8), out)).strip())


def save_packet(state, packet):
    state.counter += 1
    if state.is_test:
        return
    _type = struct.unpack('!B', packet[:1])[0]
    with open(f'packets/sample_{state.counter:04d}_{_type}.rotf{_type}', 'wb') as f:
        f.write(packet)


def encode_packet(packet):
    return struct.pack('!I', len(packet)) + packet


with open('sample_36_no_burst1.bin', 'wb') as f:
    f.write(b'$\x00\x04g\t\x00\x00\x17\x00\x00\xff\xff\xff\xff\x00')
