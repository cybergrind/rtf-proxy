meta:
  id: rotf27
  file-extension: rotf27
  endian: be
  encoding: ascii

  
seq:
  - id: p_type
    type: u1
  - id: num
    type: u2
  - id: shot_id
    type: u1
    repeat: expr
    repeat-expr: num
  - id: owner
    type: u4
    repeat: expr
    repeat-expr: num
  - id: some_byte
    type: u1
    repeat: expr
    repeat-expr: num
  - id: some_byte2
    type: u1
    repeat: expr
    repeat-expr: num
    
types:
  something:
    seq:
      - id: indicator
        type: u1
      - id: value
        type: u2
      - id: value2
        type: u2