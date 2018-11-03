AIR  = 0b00000001 # Something you can shoot through
WALL = 0b00000010 # Something you cannot walk through
ITEM = 0b00000100 # Something you can pick up
STEP = 0b00001000 # Something you can trigger by stepping on
POKE = 0b00010000 # Something you can trigger by poking
TELE = 0b00100000 # A place you can teleport to
DOOR = 0b01000000 # A place you can teleport from
PORT = 0b10000000 # Something you can shoot on

def parse(file):
  f = open(file, 'r')
  body = f.read()
  f.close()
  lines = body.split('\n')
  lines = lines[lines.index('LEVEL:')+1:]
  width = max([len(line) for line in lines])
  grid = map(lambda l: list(l.ljust(width, ' ')), lines)
  level_map = {}
  teles = {}
  spawn = None

  # Initial run through to determine portal positions
  for y, row in enumerate(grid):
    for x, char in enumerate(row):
      if char in '<>^v':
        off_x, off_y = {
          '>': (1, 0),
          '<': (-1, 0),
          '^': (0, -1),
          'v': (0, 1),
        }[char]

        label = grid[y+off_y][x+off_x]
        if label not in teles:
          teles[label] = []

        level_map[(x, y)] = (AIR|TELE, label)
        level_map[(x+off_x, y+off_y)] = (AIR|DOOR|STEP, ((1, 0), label))

        teles[label].append((x, y))

  for y, row in enumerate(grid):
    for x, char in enumerate(row):
      if (x, y) not in level_map:
        level_map[(x, y)] = (WALL, None)

      cell_type, _ = level_map[(x, y)]

      if cell_type & DOOR or cell_type & TELE:
        continue

      # Air
      if char == '.':
        level_map[(x, y)] = (AIR, None)

      # Player spawn point
      elif char == '@':
        level_map[(x, y)] = (AIR, None)
        spawn = (x, y)
      
      # Buttons
      elif char in 'rgb':
        level_map[(x, y)] = (AIR|STEP|POKE, {
          'r': 'RED',
          'g': 'GREEN',
          'b': 'BLUE',
        }[char])
      
      # Brick walls
      elif char in 'RGB':
        level_map[(x, y)] = (WALL, {
          'R': 'RED',
          'G': 'GREEN',
          'B': 'BLUE',
        }[char])

      # Portal walls
      elif char = '#':
        level_map[(x, y)] = (WALL|PORT, None)

      # Fence walls
      elif char in '-|':
        level_map[(x, y)] = (WALL|AIR, 'FENCE')

      # Shrooms
      elif char in '123':
        level_map[(x, y)] = (AIR|ITEM, char)

      # TODO X, $, 


  print('\n'.join(lines))

def read_level(x, y):
  return parse('levels/level_%d_%d' % (x, y))

class Level:
  def __init__(self, grid):
    pass