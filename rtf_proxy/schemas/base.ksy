meta:
  id: base
  file-extension: base
  endian: be
  encoding: ascii
seq:
  - id: num_fields
    type: u2
  - id: dct
    type: kv
    repeat: expr
    repeat-expr: num_fields
types:
  kv:
    seq:
      - id: key
        type: u1
      - id: value
        type:
          switch-on: key
          cases:
            0x1f: name
            0x3e: clan
            0x26: str_var
            0x36: str_var
            0x61: str_var
            0x63: str_var
            0x66: str_var
            _: int_var
  int_var:
    seq:
      - id: value
        type: u4
  name:
    seq:
      - id: size
        type: u2
      - id: name
        type: str
        size: size
  clan:
    seq:
      - id: size
        type: u2
      - id: name
        type: str
        size: size
  str_var:
    seq:
      - id: size
        type: u2
      - id: name
        type: str
        size: size