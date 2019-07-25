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
            0x1f: str_var
            0x3e: str_var
            0x26: str_var
            _: int_var
  int_var:
    seq:
      - id: value
        type: u4
  str_var:
    seq:
      - id: size
        type: u2
      - id: name
        type: str
        size: size