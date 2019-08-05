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
    
  - id: shot_ids
    type: shot_id
    repeat: expr
    repeat-expr: size
    
  - id: owners
    type: owner
    repeat: expr
    repeat-expr: size
    
  - id: always_zero
    type: unk_byte_0
    repeat: expr
    repeat-expr: size
    
  - id: shoots
    type: shot
    repeat: expr
    repeat-expr: size
    
  - id: maybe_damage
    type: unk_short
    repeat: expr
    repeat-expr: size
    
    
  - id: num_bullets
    type: num_bullets
    repeat: expr
    repeat-expr: size
    
  - id: magic
    type: magic
    repeat: expr
    repeat-expr: size
    
  - id: coords
    type: coord
    repeat: expr
    repeat-expr: size
    
    
types:
  shot_id:
    seq:
      - id: shot_id
        type: u1
  owner:
    seq:
      - id: owner
        type: u4
  coord:
    seq:
      - id: pos_x
        type: f4
      - id: pos_y
        type: f4
  unk_byte_0:
    seq:
      - id: always_zero
        type: u1
  unk_short:
    seq:
      - id: maybe_damage
        type: u2
  num_bullets:
    seq:
      - id: num_bullets
        type: u1
  magic:
    seq:
      - id: magic_3e20d97c
        type: u4
  shot:
    seq:
      - id: maybe_shot_id
        type: u4
     