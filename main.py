#!/usr/bin/env python3

import pygame, time, math
pygame.init()

import config
screen = pygame.display.set_mode([config.WIDTH, config.HEIGHT], pygame.RESIZABLE)

import level
from util import SPRITE_SIZE, load_sprite, cut_sheet, draw_sprite

pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)

# Put loading screen stuff here
pygame.draw.rect(screen, (255, 255, 255), (0, 0, config.WIDTH, config.HEIGHT))
pygame.display.update()

PLAYER_TOP_SPRITE = cut_sheet(level.SPRITES, 0, 6, scale=4)
PLAYER_BOTTOM_SPRITE = cut_sheet(level.SPRITES, 0, 7, scale=4)

levels = level.crawl_rooms()

def set_level(pos):
  global current_level, neighbors, current_pos
  current_pos = pos
  current_level, neighbors = levels[pos] # Start in 0, 0

  for loc in [pos] + neighbors:
    level, _ = levels[loc]
    level.preload()

def get_tile(x, y):
  return current_level.grid[(int(player_pos['x']+x), int(player_pos['y']+y))]

def can_collide(x, y):
  tile = get_tile(x, y)
  if not tile.COLORED:
    return not tile.is_wall()
  return not tile.is_wall() or current_level.timers.get(tile.color.value, 0) > current_level.last_render

tick = time.time()
lastTick = tick
running = True

set_level((0, 0))

player_pos = {
  'x': current_level.spawn.location[0],
  'y': current_level.spawn.location[1],
  'vx': 0,
  'vy': 0,
}

while running:
  lastTick, tick = tick, time.time()
  delta = tick - lastTick

  keys = pygame.key.get_pressed()

  if keys[pygame.K_ESCAPE]:
    running = False
    break

  keyPressed = {}


  for event in pygame.event.get():
    if event.type == pygame.QUIT:
      running = False

    if event.type == pygame.VIDEORESIZE:
      config.WIDTH, config.HEIGHT = event.dict['size']
      screen = pygame.display.set_mode((config.WIDTH, config.HEIGHT), pygame.RESIZABLE)

    if event.type == pygame.KEYDOWN: # assign the key if it's down
      keyPressed[event.dict['key']] = True

  vel_x, vel_y = player_pos['vx'], player_pos['vy']

  # if keys[pygame.K_w] and vel_y == 0:
  #   vel_y = -0.2

  if can_collide(0, 1):
    vel_y += delta * config.GRAVITY
    # vel_y = 0.1

  vel_y = max(min(0.3, vel_y), -0.3)

  if not can_collide(0.5, -1 + vel_y): # Check if we're falling into a block
    if player_pos['y'] + vel_y < int(player_pos['y']):
      player_pos['y'] = int(player_pos['y'])
      vel_y = 0

  if not can_collide(0.5, 1 + vel_y): # Check if we're falling into a block
    if player_pos['y'] + vel_y > int(player_pos['y']):
      player_pos['y'] = int(player_pos['y']) + 1
      vel_y = 0

  # Severely limit air control
  if keys[pygame.K_a]:
    vel_x = -delta * config.WALK_SPEED

  if keys[pygame.K_d]:
    vel_x = delta * config.WALK_SPEED

  # Jumping is floating atm
  # if keys[pygame.K_SPACE]:
    # vel_y = -delta * config.JUMP_VELOCITY

    # vel_x = vel_x - vel_x * config.FRICTION * delta

  
  if abs(vel_x) > 0: # Check if we're moving left/right
    # Moving right
    if vel_x > 0 and not can_collide(1, 0):
      # Check if we would move into the block
      if player_pos['x'] + vel_x > int(player_pos['x'] + 0.5):
        # Just don't move into the block
        player_pos['x'] = int(player_pos['x'])
        vel_x = 0

    # Moving left
    elif not can_collide(-1, 0):
      # Check if we would move into the block
      if player_pos['x'] - 1 + vel_x < int(player_pos['x'] - 1):
        # Just don't move into the block
        player_pos['x'] = int(player_pos['x'])
        vel_x = 0

  player_pos['x'] += vel_x
  player_pos['y'] += vel_y
  vel_x = 0

  player_pos['vx'], player_pos['vy'] = vel_x, vel_y

  player_x = int(player_pos['x'] * SPRITE_SIZE * 4)
  player_y = int(player_pos['y'] * SPRITE_SIZE * 4)

  x_off = -player_x + (config.WIDTH >> 1)
  y_off = -player_y + (config.HEIGHT >> 1)

  if get_tile(0.5, 0.5).MASK & level.STEP:
    tile = get_tile(0.5, 0.5)
    if tile.COLORED:
      color = tile.color.value
      if current_level.timers.get(color, 0) < tick + config.TIMER_DURATION - 1:
        current_level.start_timer(color)
        current_level.update_sprite()
    elif tile.TELE:
      # Coord of tele entrance
      x, y = tile.direction
      pos = (int(player_pos['x'] - x + 0.5), int(player_pos['y'] - y + 0.5))
      # Index of tele entrance
      index = current_level.teles[(tile.label, tile.direction)].index(pos)

      curr_x, curr_y = current_pos
      # with the coord of the next level, get the next level
      next_level, _ = levels[(curr_x + x, curr_y + y)]
      # Find the complement tele exit
      dest_pos = next_level.teles[(tile.label, (-x, -y))][index]

      # Update player position and level
      set_level((curr_x + x, curr_y + y))
      player_pos['x'], player_pos['y'] = dest_pos
 
  pygame.draw.rect(screen, (0, 0, 0), (0, 0, config.WIDTH, config.HEIGHT))
  current_level.render(screen, bg=True, mg=True, x_off=x_off, y_off=y_off)

  draw_sprite(screen, PLAYER_TOP_SPRITE, player_x + x_off, player_y - SPRITE_SIZE * 4 + y_off)
  draw_sprite(screen, PLAYER_BOTTOM_SPRITE, player_x + x_off, player_y + y_off)
  # tickGame(delta, keys)
  # drawGame()

  current_level.render(screen, fg=True, x_off=x_off, y_off=y_off)
  pygame.display.update()
