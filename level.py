from enum import Enum

AIR  = 0b00000001 # Something you can shoot through
WALL = 0b00000010 # Something you cannot walk through
ITEM = 0b00000100 # Something you can pick up
STEP = 0b00001000 # Something you can trigger by stepping on
POKE = 0b00010000 # Something you can trigger by poking
GRID = 0b00100000 # Something you can shoot portals on

from util import load_sprite

# A cell in the level
class Tile:
  MASK = 0
  SYMBOL = ' '

  def __str__(self):
    return self.SYMBOL

# Walls players cannot walk into
class WallTile(Tile):
  MASK = WALL
  SYMBOL = ' '

# Nothing tile, players can walk through this
class AirTile(Tile):
  MASK = AIR
  SYMBOL = '.'

# Location where player will spawn
class SpawnTile(Tile):
  MASK = AIR
  SYMBOL = '@'

  def __init__(self, location):
    self.location = location

# Color enum
class WallColor(Enum):
  RED = 0b001
  BLUE = 0b010
  GREEN = 0b100
  PURPLE = RED | BLUE
  CYAN = GREEN | BLUE
  YELLOW = RED | GREEN

# Togglable wall
class ColorWallTile(Tile):
  MASK = WALL
  SYMBOL = 'W'

  def __init__(self, color):
    if not isinstance(color, WallColor): raise Exception('Invalid Wall Color')
    self.color = color

  def __str__(self):
    return {
      (WallColor.RED): 'R',
      (WallColor.BLUE): 'B',
      (WallColor.GREEN): 'G',
      (WallColor.PURPLE): 'P',
      (WallColor.CYAN): 'C',
      (WallColor.YELLOW): 'Y',
    }[self.color]

# Togglable button
class ColorButtonTile(Tile):
  SYMBOL = 'w'
  MASK = AIR | STEP | POKE

  def __init__(self, color):
    if not isinstance(color, WallColor): raise Exception('Invalid Button Color')
    self.color = color

  def __str__(self):
    return {
      (WallColor.RED): 'r',
      (WallColor.BLUE): 'b',
      (WallColor.GREEN): 'g',
      (WallColor.PURPLE): 'p',
      (WallColor.CYAN): 'c',
      (WallColor.YELLOW): 'y',
    }[self.color]

# Win objective item
class LootTile(Tile):
  MASK = AIR | STEP | ITEM | POKE
  SYMBOL = '$'

# Place where players teleport to from other rooms
class TeleExitTile(Tile):
  MASK = AIR
  SYMBOL = '>'

  def __init__(self, label, direction):
    self.label = label
    self.direction = direction

  def __str__(self):
    return {
      (1, 0): '>',
      (-1, 0): '<',
      (0, -1): '^',
      (0, 1): 'v',
    }[self.direction] or '?'

# Walk into this to teleport to a different room
class TeleEntranceTile(Tile):
  MASK = AIR | STEP
  SYMBOL = '*'

  def __init__(self, label, direction):
    self.label = label
    self.direction = direction

  def __str__(self):
    return self.label

# Clears the player's portals
class PortalClearTile(Tile):
  SYMBOL = 'X'
  MASK = AIR | STEP

# A spot where players can shoot portals
class GridTile(Tile):
  SYMBOL = '#'
  MASK = WALL | GRID

# A fence
class FenceTile(Tile):
  SYMBOL = '-'
  MASK = WALL | AIR

# Shroom ability enum
class ShroomType(Enum):
  JUMP = 0b001
  BLINK = 0b010
  GRAVITY = 0b100

# Shroom item
class ShroomTile(Tile):
  SYMBOL = '1'
  MASK = AIR | ITEM | POKE | STEP

  def __init__(self, type):
    if not isinstance(type, ShroomType): raise Exception('Invalid Shroom Type')
    self.type = type

  def __str__(self):
    return str(self.type.value)

# Creates a level map from a file
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
        key = (label, (off_x, off_y))
        if key not in teles:
          teles[key] = []

        # Create tele tiles
        level_map[(x, y)] = TeleExitTile(label, (off_x, off_y))
        level_map[(x+off_x, y+off_y)] = TeleEntranceTile(label, (off_x, off_y))

        # Create links for room crawling
        teles[key].append((x, y))

  # Fill in other tiles
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

  return (level_map, (width, height), teles, spawn)

# Parses a level from coords
def read_level(x, y):
  return parse('levels/level_%d_%d' % (y, x))

# Creates a level object from coords
def get_level(x, y):
  (grid, (width, height), teles, spawn) = read_level(x, y)
  return Level((x, y), grid, (width, height), teles, spawn)


class Level:
  def __init__(self, pos, grid, size, teles, spawn):
    self.pos = pos
    self.spawn = spawn
    self.width, self.height = size

    # Tele exit positions
    self.teles = teles

    # Tile grid
    self.grid = grid

    # Level has generated sprites
    self.loaded = False

  # Determines the adjacent rooms based on teles inside the room
  def get_neighbors(self):
    x, y = self.pos
    return list(set([(x + off_x, y + off_y) for label, (off_x, off_y) in self.teles]))

  def preload(self):
    if self.loaded:
      return

    # TODO generate  screens for the level
    self.loaded = True

  # Prints out the room in ascii notation
  def __str__(self):
    return '\n'.join([
      ''.join([
        str(self.grid[(x, y)]) for x in range(self.width)
      ]) for y in range(self.height)
    ])

  def __repr__(self):
    return '<Room @ (%d, %d)>' % self.pos

# Finds all the linked rooms
def crawl_rooms(debug=False):
  levels = {}
  undiscovered, discovered = [(0, 0)], []

  # Pop undiscovered rooms from a queue to conduct a breadth first scan
  while len(undiscovered):
    (x, y), undiscovered = undiscovered[0], undiscovered[1:]
    discovered.append((x, y))
    level = get_level(x, y)

    if debug:
      print('Exploring Room %s,%s' % (x, y))
      print(str(level))

    links = level.get_neighbors()
    levels[(x, y)] = (level, links)

    # Add explored rooms to our to-explore queue
    for (x, y) in links:
      if (x, y) not in discovered and (x, y) not in undiscovered:
        undiscovered.append((x, y))

  if debug:
    print(levels)

  return levels

# crawl_rooms(debug=True)