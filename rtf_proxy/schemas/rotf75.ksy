meta:
  id: rotf75
  file-extension: rotf75
  endian: be
  encoding: ascii

  
seq:
  - id: p_type
    type: u1
  - id: size
    type: u2
  - id: shoots
    type: shot
    repeat: expr
    repeat-expr: size
    
    
types:
  shot:
    seq:
      - id: shot_type
        type: u1
      - id: who
        type: u4
      - id: angle
        type: f4
      - id: unknown_flag
        type: u4
      - id: unknown_flag2
        type: u4
      - id: pos_x
        type: u4
      - id: pos_y
        type: u4