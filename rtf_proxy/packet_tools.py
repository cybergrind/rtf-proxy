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


def payload_to_packet(payload):
    return struct.pack('!I', len(payload) + 4) + payload


with open('sample_85.snake.rotf85', 'wb') as f:
    f.write(b'U\x00\x00\x01\xbc\x00\x00\x00d\x00N\x00\x04e`C\xe3t\xaaD\x86\xffd\x00\x02\x01\x00\x00\x02\xd8\x04\x00\x00\x01\x04\x00\x04p<C\xdf\x8b\xaaD\x88\xdbm\x00\x00\x00\x04o+C\xe0\r?D\x88\xcd\x14\x00\x01\x01\x00\x00\x03c\x00\x04k\xf0De\x13\xb9Dj_"\x00\x01\x04\x00\x00\x00\x9b\x00\x04n$Dh@\x96DiLl\x00\x02\x01\x00\x00\x03\xab\x04\x00\x00\x01h\x00\x04l\x19Dd\xb9\xbfDj\xe2\xab\x00\x00\x00\x04h\xedC\xe7\xearD\x88\xd7\x08\x00\x01\x01\x00\x00\x02\xdf\x00\x04k6C\xe4\x13FD\x86\xb0\xec\x00\x02\x01\x00\x00\x01\x15\x04\x00\x00\x00c\x00\x04d\xb9Dc\xf5\xd7Dj\n\xf9\x00\x01\x01\x00\x00\x02h\x00\x04o\x8eD\x90\xcamDft\xd1\x00\x01\x04\x00\x00\x01\x1b\x00\x04d\xc6DE0\x8bD\xbb\xe4[\x00\x01\x01\x00\x00\x01\n\x00\x04o\xa0C\xe1\x91cD\x87m\xfe\x00\x00\x00\x045\x13D 2\xefD\x11\x96\xb6\x00\x00\x00\x04pIDc\xdeHDj\xc81\x00\x01\x01\x00\x00\x02x\x00\x04o\xa7C\xe1\xb2~D\x88\x18\xcb\x00\x00\x00\x04o\xa9C\xde\x99\xccD\x88\x91\xb7\x00\x00\x00\x04o\xacDq\x13|DV(\x0e\x00\x00\x00\x04o\xadC\xe5\x90DD\x88\xba\x8f\x00\x01\x01\x00\x00\x03\x9b\x00\x04jFC\xe0\xc3pD\x88\xac\xce\x00\x02\x01\x00\x00\x03\x10\x04\x00\x00\x00x\x00\x04o\xb3C\xe2q\x7fD\x88\xaa\x9a\x00\x02\x01\x00\x00\x02\xd1\x04\x00\x00\x00\xd1\x00\x04ltC\xe1\xf5\x8fD\x87\xad\xfd\x00\x00\x00\x04o\xb5C\xdf\xa6\xf0D\x87m\r\x00\x01\x04\x00\x00\x00\x9d\x00\x04kaDhi\x80Di\x8d\xa3\x00\x01\x04\x00\x00\x00\xc6\x00\x04n\xa6C\xe1\xa3iD\x87\xd4s\x00\x02\x04\x00\x00\x00V\x01\x00\x00\x03\x08\x00\x04t\x91C\xe2 UD\x88\xc1s\x00\x01\x01\x00\x00\x04\x12\x00\x04o\xbeC\xe8+pD\x8a\x15\xeb\x00\x00\x00\x04pNDm#\rD_\x9a\x8e\x00\x01\x04\x00\x00\x00\x8e\x00\x04kkC\xdfA\xb0D\x88\xc9\x06\x00\x01\x04\x00\x00\x01\x9a\x00\x04o\xc1C\xe3\xb1\xdeD\x88\xe5\xef\x00\x00\x00\x04o\xc3C\xdf6nD\x88\xea\x0b\x00\x00\x00\x04o\xc4C\xe4\'\xb3D\x89-\xb1\x00\x01\x04\x00\x00\x022\x00\x04o\xc5C\xe0Y\xc8D\x88\xe6b\x00\x02\x01\x00\x00\x02]\x04\x00\x00\x00G\x00\x04o\xc9C\xe6\xfeMD\x893\x07\x00\x02\x01\x00\x00\x02-\x04\x00\x00\x00@\x00\x04l\x8bC\xe0\xf02D\x88\x0b\x80\x00\x01\x01\x00\x00\x02I\x00\x04o\xd4D\x84\x9e\x10DY\xf2\x06\x00\x00\x00\x04o\xd5C\xe4&\xf4D\x89\t\xeb\x00\x00\x00\x04n\xc0Dg\xe1QDg\x84\xc9\x00\x00\x00\x04o\xd6D\x9eY\nDny\x16\x00\x00\x00\x04o\xd7C\xe08sD\x88*\xa8\x00\x01\x04\x00\x00\x00\xf1\x00\x04o\xd9C\xe3\xca\xc2D\x87?\xae\x00\x01\x01\x00\x00\x00\xd0\x00\x04p9Do\x86\xcfDbE\x1d\x00\x01\x01\x00\x00\x01\xe1\x00\x04o\xdfC\xe2nWD\x88\x91\x10\x00\x01\x01\x00\x00\x03\x8d\x00\x04n\xcaC\xea,\x8eD\x89t\xd0\x00\x01\x04\x00\x00\x012\x00\x04f&D\x850xDP(G\x00\x01\x01\x00\x00\x02\xdb\x00\x04pdDU\x8b\xe0DlSD\x00\x00\x00\x04k\xacDgaGDf~$\x00\x01\x01\x00\x00\x024\x00\x04p\xcaC\xdd\x849D\x89b\xf6\x00\x02\x01\x00\x00\x02\xb7\x04\x00\x00\x00G\x00\x04pFC\xe1chD\x87\x8a\xa1\x00\x01\x04\x00\x00\x00S\x00\x04m\xf5C\xe7]BD\x88\xb6\xf8\x00\x01\x01\x00\x00\x03\xa8\x00\x04tkC\xe3zTD\x89\x06e\x00\x00\x00\x04p\xd0Du\xc8\xceD\x81{\xde\x00\x00\x00\x04p@C\xe6\'\xfeD\x87\xe0\xc3\x00\x01\x01\x00\x00\x02\xd7\x00\x04t\x94C\xe4\xca\x07D\x89).\x00\x00\x00\x04o\xebC\xe2\r\'D\x88(\xbe\x00\x01\x01\x00\x00\x05\xdc\x00\x04piC\xe2\x16\xc2D\x88\x8d\x7f\x00\x02\x01\x00\x00\x03\x15\x04\x00\x00\x00\xff\x00\x04t_C\xe3\x86ND\x88\xf6\xbd\x00\x00\x00\x04t\x93C\xe3\x87YD\x87+\xad\x00\x01\x01\x00\x00\x02R\x00\x04p^DX\xcfxDm`k\x00\x01\x01\x00\x00\x01\x06\x00\x04o\xefC\xe60MD\x88\xc0\xa2\x00\x02\x01\x00\x00\x08F\x04\x00\x00\x00\xad\x00\x04pEC\xd9\xfa\xc6D\x88\xedI\x00\x02\x01\x00\x00\x02\x8a\x04\x00\x00\x00\xb8\x00\x04tRD\x18\x89[D\xe5*V\x00\x00\x00\x04p|C\xde\xce\xd7D\x88\xa59\x00\x00\x00\x04p\x80C\xdfO\xb6D\x8922\x00\x02\x01\x00\x00\x01\xd9\x04\x00\x00\x00\xa0\x00\x04t\x92C\xe2\t\x92D\x88\xbc\xeb\x00\x02\x04\x00\x00\x01i\x01\x00\x00\t\xfc\x00\x04p}C\xe0i\xeaD\x88+\xb4\x00\x02\x01\x00\x00\x06\x97\x04\x00\x00\x00~\x00\x04p=C\xe36\x1bD\x88\xe2\x17\x00\x02\x01\x00\x00\x02\xaf\x04\x00\x00\x00\x0c\x00\x04pWC\xdf\'\xd4D\x88\xf0\x0c\x00\x02\x01\x00\x00\x02U\x04\x00\x00\x01\x11\x00\x04p\xa6DdJ\x80Dj\x08\xcf\x00\x01\x01\x00\x00\x00H\x00\x045\xe5D\x1f\x8bND\x13\x9b\x00\x00\x00\x00\x04t\xa1D{\xca\xd2Dv\xee\xf3\x00\x01\x01\x00\x00\x08\x17\x00\x04p4DjC\xa3Di$\xd8\x00\x00\x00\x043\x9dD\x1d\x01}D\x11\xcc\xa5\x00\x00\x00\x04tNC\xe3\xc7\xbfD\x88\xab\xc9\x00\x02\x01\x00\x00\x05Q\x04\x00\x00\x01\xc7\x00\x04t\xaeC\xe1\x00\x00D\x88.\xad\x00\x00\x00\x04p\x85C\xe0\xf9\x86D\x86\xa3\xb7\x00\x01\x01\x00\x00\x00\xb6\x00\x04p\xa3C\xe2E\x82D\x88\xec{\x00\x01\x01\x00\x00\x01\x92\x00\x04o\xfdC\xe0}ID\x88s]\x00\x00\x00\x04t\xa0C\xe3h\xbbD\x87\xb1X\x00\x01\x01\x00\x00\x02\xfc')
    
