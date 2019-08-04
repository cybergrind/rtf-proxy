meta:
  id: rotf79
  imports:
    - base
  file-extension: rotf79
  endian: be
  encoding: ascii

seq:
  - id: p_type
    type: u1
  - id: terrain_size
    type: u2
  - id: maybe_terrain_info
    type: unk
    repeat: expr
    repeat-expr: terrain_size
  - id: num_entries
    type: u2
  - id: entries
    type: entry
    repeat: expr
    repeat-expr: num_entries
  - id: num_gone_objects
    type: u2
  - id: gone_object_ids
    type: u4
    repeat: expr
    repeat-expr: num_gone_objects
  - id: end_entity
    type: base
  - id: rest
    size-eos: true
types:
  unk:
    seq:
      - id: unk_s
        type: u2
      - id: unk_s2
        type: u2
      - id: unk_s3
        type: u2
  entry:
    seq:
      - id: obj_type
        type: u2
      - id: id
        type: u4
      - id: pos_x
        type: u4
      - id: pos_y
        type: u4
      - id: object
        type: base