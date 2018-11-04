from enum import Enum

AIR  = 0b00000001 # Something you can shoot through
WALL = 0b00000010 # Something you cannot walk through
ITEM = 0b00000100 # Something you can pick up
STEP = 0b00001000 # Something you can trigger by stepping on
POKE = 0b00010000 # Something you can trigger by poking
GRID = 0b00100000 # Something you can shoot portals on

class Tile:
  MASK = 0
  SYMBOL = ' '

class WallTile(Tile):
  MASK = WALL
  SYMBOL = ' '

class AirTile(Tile):
  MASK = AIR
  SYMBOL = '.'

class SpawnTile(Tile):
  MASK = AIR
  SYMBOL = '@'

  def __init__(self, location):
    self.location = location

class WallColor(Enum):
  RED = 0b001
  BLUE = 0b010
  GREEN = 0b100
  PURPLE = RED | BLUE
  CYAN = GREEN | BLUE
  YELLOW = RED | GREEN

class ColorWallTile(Tile):
  MASK = WALL
  SYMBOL = 'W'

  def __init__(self, color):
    if not isinstance(color, WallColor): raise Exception('Invalid Wall Color')
    self.color = color

class ColorButtonTile(Tile):
  SYMBOL = 'w'
  MASK = AIR | STEP | POKE

  def __init__(self, color):
    if not isinstance(color, WallColor): raise Exception('Invalid Button Color')
    self.color = color

class LootTile(Tile):
  MASK = AIR | STEP | POKE
  SYMBOL = '$'

class TeleExitTile(Tile):
  MASK = AIR
  SYMBOL = '>'

  def __init__(self, label):
    self.label = label

class TeleEntranceTile(Tile):
  MASK = AIR | STEP
  SYMBOL = '*'

  def __init__(self, label, destination):
    self.label = label
    self.destination = destination

class PortalClearTile(Tile):
  SYMBOL = 'X'
  MASK = AIR | STEP

class GridTile(Tile):
  SYMBOL = '#'
  MASK = WALL | GRID

class FenceTile(Tile):
  SYMBOL = '-'
  MASK = WALL | AIR

class ShroomType(Enum):
  JUMP = 0b001
  BLINK = 0b010
  GRAVITY = 0b100

class ShroomTile(Tile):
  SYMBOL = '1'
  MASK = AIR | ITEM | POKE | STEP

  def __init__(self, type):
    if not isinstance(type, ShroomType): raise Exception('Invalid Shroom Type')
    self.type = type

def parse(file):
  f = open(file, 'r')
  body = f.read()
  f.close()
  lines = body.split('\n')
  lines = lines[lines.index('LEVEL:')+1:]
  line_width = max([len(line) for line in lines])
  grid = list(map(lambda l: list(' ' + l.ljust(line_width + 1, ' ')), [''] + lines + ['']))
  level_map = {}
  teles = {}
  spawn = None

  height, width = len(grid), len(grid[0])

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

        level_map[(x, y)] = TeleExitTile(label)
        level_map[(x+off_x, y+off_y)] = TeleEntranceTile(label, (off_x, off_y))

        teles[label].append((x, y))

  for y, row in enumerate(grid):
    for x, char in enumerate(row):
      if (x, y) not in level_map:
        level_map[(x, y)] = WallTile()

      cell = level_map[(x, y)]

      if cell and not isinstance(cell, WallTile):
        continue

      # Air
      if char == '.':
        level_map[(x, y)] = AirTile()

      # Player spawn point
      elif char == '@':
        spawn = level_map[(x, y)] = SpawnTile((x, y))

      # Portal clear
      elif char == 'X':
        spawn = level_map[(x, y)] = PortalClearTile()
      
      # Loot
      elif char == '$':
        spawn = level_map[(x, y)] = LootTile()
      
      # Buttons
      elif char in 'rgbpcy':
        level_map[(x, y)] = ColorButtonTile({
          'r': WallColor.RED,
          'g': WallColor.GREEN,
          'b': WallColor.BLUE,
          'p': WallColor.PURPLE,
          'c': WallColor.CYAN,
          'y': WallColor.YELLOW,
        }[char])
      
      # Brick walls
      elif char in 'RGB':
        level_map[(x, y)] = ColorWallTile({
          'R': WallColor.RED,
          'G': WallColor.GREEN,
          'B': WallColor.BLUE,
          'P': WallColor.PURPLE,
          'C': WallColor.CYAN,
          'Y': WallColor.YELLOW,
        }[char])

      # Portal walls
      elif char == '#':
        level_map[(x, y)] = GridTile()

      # Fence walls
      elif char in '-|':
        level_map[(x, y)] = FenceTile()

      # Shrooms
      elif char in '123':
        level_map[(x, y)] = ShroomTile({
          '1': ShroomType.JUMP,
          '2': ShroomType.BLINK,
          '3': ShroomType.GRAVITY,
        }[char])

  # print('\n'.join([
  #   ''.join([
  #     level_map[(x, y)].SYMBOL for x in range(width)
  #   ]) for y in range(height)
  # ]))

  return level_map

def read_level(x, y):
  return parse('levels/level_%d_%d' % (x, y))

class Level:
  def __init__(self, grid):
    pass

# print(parse('/home/cake/Github/meshiest/recollect/levels/level_0_0'))