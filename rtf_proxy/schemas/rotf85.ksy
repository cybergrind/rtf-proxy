meta:
  id: rotf85
  imports:
    - base
  file-extension: rotf85
  endian: be
  encoding: ascii

seq:
  - id: p_type
    type: u1
  - id: ts
    type: u8
  - id: num_entries
    type: u2
  - id: entries
    type: entry
    repeat: expr
    repeat-expr: num_entries
  - id: rest
    size-eos: true
    
types:
  entry:
    meta:
      title: TTTT
    seq:
      - id: id
        type: u4
      - id: x_pos
        type: u4
      - id: y_pos
        type: u4
      - id: object
        type: base
