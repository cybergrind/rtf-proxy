meta:
  id: base
  file-extension: base
  endian: be
  encoding: ascii

types:
  base:
    seq:
      - id: num_fields
        type: u2
      - id: dict
        type: kv
        repeat: expr
        repeat-expr: num_fields
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
      - id: clan_name
        type: str
        size: size
  str_var:
    seq:
      - id: size
        type: u2
      - id: name
        type: str
        size: size