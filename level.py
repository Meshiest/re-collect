from enum import Enum, IntEnum

AIR  = 0b00000001 # Something you can shoot through
WALL = 0b00000010 # Something you cannot walk through
ITEM = 0b00000100 # Something you can pick up
STEP = 0b00001000 # Something you can trigger by stepping on
POKE = 0b00010000 # Something you can trigger by poking
GRID = 0b00100000 # Something you can shoot portals on

from util import load_sprite, cut_sheet, draw_sprite, level_surface, SPRITE_SIZE
import pygame, time, config

SPRITES = load_sprite('level_sprites.png')
GRASS_SPRITE = cut_sheet(SPRITES, 5, 1)

# A cell in the level
class Tile:
  MASK = 0
  SYMBOL = ' '
  BG = False
  FG = False
  MG = False
  COLORED = False
  STICKY = False
  TELE = False
  SPRITE = cut_sheet(SPRITES, 7, 0)

  def is_air(self):
    return self.MASK & AIR

  def is_wall(self):
    return self.MASK & WALL

  def sprite(self):
    return self.SPRITE

  def __str__(self):
    return self.SYMBOL

# Walls players cannot walk into
class WallTile(Tile):
  MASK = WALL
  SYMBOL = ' '
  SPRITE = cut_sheet(SPRITES, 5, 0)
  BG = True

# Nothing tile, players can walk through this
class AirTile(Tile):
  MASK = AIR
  SYMBOL = '.'
  BG = True

# Location where player will spawn
class SpawnTile(Tile):
  MASK = AIR
  SYMBOL = '@'

  def __init__(self, location):
    self.location = location

# Color enum
class WallColor(IntEnum):
  RED = 0b001
  GREEN = 0b010
  BLUE = 0b100
  PURPLE = RED | BLUE
  CYAN = GREEN | BLUE
  YELLOW = RED | GREEN

# Togglable wall
class ColorWallTile(Tile):
  MASK = WALL
  SYMBOL = 'W'
  RED_SPRITE = cut_sheet(SPRITES, 0, 0)
  GREEN_SPRITE = cut_sheet(SPRITES, 1, 0)
  BLUE_SPRITE = cut_sheet(SPRITES, 2, 0)
  COLORED = True
  MG = True

  def __init__(self, color):
    if not isinstance(color, WallColor): raise Exception('Invalid Wall Color')
    self.color = color

  def sprite(self):
    if self.color & WallColor.RED:
      return self.RED_SPRITE
    elif self.color & WallColor.GREEN:
      return self.GREEN_SPRITE
    elif self.color & WallColor.BLUE:
      return self.BLUE_SPRITE
    return self.RED_SPRITE

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
  RED_SPRITE = cut_sheet(SPRITES, 0, 1)
  RED_PRESSED_SPRITE = cut_sheet(SPRITES, 0, 2)
  GREEN_SPRITE = cut_sheet(SPRITES, 1, 1)
  GREEN_PRESSED_SPRITE = cut_sheet(SPRITES, 1, 2)
  BLUE_SPRITE = cut_sheet(SPRITES, 2, 1)
  BLUE_PRESSED_SPRITE = cut_sheet(SPRITES, 2, 2)
  COLORED = True
  MG = True
  STICKY = True

  def __init__(self, color):
    if not isinstance(color, WallColor): raise Exception('Invalid Button Color')
    self.color = color

  def sprite(self, pressed=False):
    if self.color & WallColor.RED:
      return pressed and self.RED_PRESSED_SPRITE or self.RED_SPRITE
    elif self.color & WallColor.GREEN:
      return pressed and self.GREEN_PRESSED_SPRITE or self.GREEN_SPRITE
    elif self.color & WallColor.BLUE:
      return pressed and self.BLUE_PRESSED_SPRITE or self.BLUE_SPRITE
    return pressed and self.RED_PRESSED_SPRITE or self.RED_SPRITE

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
  MG = True

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
  TELE = True
  SYMBOL = '*'
  SPRITE_RIGHT = cut_sheet(SPRITES, 0, 4)
  SPRITE_LEFT = pygame.transform.flip(SPRITE_RIGHT, True, False)
  SPRITE_UP = pygame.transform.rotate(SPRITE_RIGHT, 90)
  SPRITE_DOWN = pygame.transform.flip(SPRITE_UP, False, True)
  FG = True

  def __init__(self, label, direction):
    self.label = label
    self.direction = direction

  def sprite(self):
    return {
      (1, 0): self.SPRITE_RIGHT,
      (-1, 0): self.SPRITE_LEFT,
      (0, 1): self.SPRITE_DOWN,
      (0, -1): self.SPRITE_UP,
    }[self.direction]

  def __str__(self):
    return self.label

# Clears the player's portals
class PortalClearTile(Tile):
  SYMBOL = 'X'
  MASK = AIR | STEP
  SPRITE = cut_sheet(SPRITES, 4, 0)
  FG = True

# A spot where players can shoot portals
class GridTile(Tile):
  SYMBOL = '#'
  MASK = WALL | GRID
  SPRITE = cut_sheet(SPRITES, 6, 0)
  BG = True

# A fence
class FenceTile(Tile):
  SYMBOL = '-'
  MASK = WALL | AIR
  SPRITE = cut_sheet(SPRITES, 3, 0)
  FG = True

# Shroom ability enum
class ShroomType(IntEnum):
  JUMP = 0b001
  BLINK = 0b010
  GRAVITY = 0b100

# Shroom item
class ShroomTile(Tile):
  SYMBOL = '1'
  MASK = AIR | ITEM | POKE | STEP
  JUMP_SPRITE = cut_sheet(SPRITES, 0, 3)
  GRAVITY_SPRITE = cut_sheet(SPRITES, 1, 3)
  BLINK_SPRITE = cut_sheet(SPRITES, 2, 3)
  MG = True
  STICKY = True

  def __init__(self, type):
    if not isinstance(type, ShroomType): raise Exception('Invalid Shroom Type')
    self.type = type

  def sprite(self):
    if self.type & ShroomType.JUMP:
      return self.JUMP_SPRITE
    elif self.type & ShroomType.GRAVITY:
      return self.GRAVITY_SPRITE
    elif self.type & ShroomType.BLINK:
      return self.BLINK_SPRITE
    return self.JUMP_SPRITE

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
        level_map[(x, y)] = PortalClearTile()
      
      # Loot
      elif char == '$':
        level_map[(x, y)] = LootTile()
      
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

    # Timers for colored buttons
    self.timers = {}
    self.last_render = 0

    # Background sprite
    self.bg_sprite = None
    # Middleground sprite (Interactivity)
    self.mg_sprite = None
    # Foreground sprite
    self.fg_sprite = None

  def start_timer(self, timer):
    self.timers[timer] = time.time() + config.TIMER_DURATION

  def update_sprite(self):
    firstRender = False
    
    if not self.bg_sprite:
      firstRender = True
      bg = self.bg_sprite = level_surface(self.width, self.height)

    mg = self.mg_sprite = level_surface(self.width, self.height)

    if not self.fg_sprite:
      fg = self.fg_sprite = level_surface(self.width, self.height)

    for x in range(self.width):
      for y in range(self.height):
        tile = self.grid[(x, y)]
        # TODO check if a tile has "Sticky" prop and rotate to stick to the nearest wall
        isAir = tile.is_air()
        sprite = tile.sprite()
        timerOn = False

        if tile.COLORED:
          timerOn = self.timers.get(tile.color.value, 0) > self.last_render

          if tile.MASK & STEP:
            sprite = tile.sprite(timerOn)

        if tile.STICKY:
          if not self.grid[(x, y+1)].is_air():
            pass
          elif not self.grid[(x+1, y)].is_air():
            sprite = pygame.transform.rotate(sprite, 90)
          elif not self.grid[(x-1, y)].is_air():
            sprite = pygame.transform.rotate(sprite, 270)
          elif not self.grid[(x, y-1)].is_air():
            sprite = pygame.transform.rotate(sprite, 180)

        # Avoid re-rendering bg
        if firstRender:
          if isAir or tile.MG and tile.MASK & WALL:
            draw_sprite(bg, AirTile.SPRITE, x, y, scale=True)

          if tile.BG:
            draw_sprite(bg, sprite, x, y, scale=True)

          # Draw grass if current tile is air and below is not air
          if isAir and not self.grid[(x, y+1)].MASK & AIR:
            draw_sprite(bg, GRASS_SPRITE, x, y, scale=True)

          if tile.FG:
            draw_sprite(fg, sprite, x, y, scale=True)

        # render if there's a timer on and it's not a wall, or there's not timer on
        if tile.MG and (not timerOn or (tile.COLORED and tile.MASK & AIR)):
          draw_sprite(mg, sprite, x, y, scale=True)



  # Determines the adjacent rooms based on teles inside the room
  def get_neighbors(self):
    x, y = self.pos
    return list(set([(x + off_x, y + off_y) for label, (off_x, off_y) in self.teles]))

  def render(self, screen, bg=False, mg=False, fg=False, x_off=0, y_off=0):
    last_render = self.last_render
    now = self.last_render = time.time()

    def render_sprite(sprite):
      sprite = pygame.transform.scale(sprite, (sprite.get_width() * 4, sprite.get_height() * 4))
      x, y, width, height = sprite.get_rect()
      screen.blit(sprite, (x + x_off, y + y_off, width, height))

    if bg:
      render_sprite(self.bg_sprite)

    if mg:
      # Check if any of our timers expired to update the frame
      for t in self.timers:
        timer = self.timers[t]
        if timer > 0 and timer < now:
          self.update_sprite()
          self.timers[t] = 0
          break

      render_sprite(self.mg_sprite)

    if fg:
      render_sprite(self.fg_sprite)


  def preload(self):
    if self.loaded:
      return

    self.update_sprite()
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