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
  - id: counter
    type: u4
  - id: timeout
    type: u4
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
      - id: pos_x
        type: f4
      - id: pos_y
        type: f4
      - id: object
        type: base
