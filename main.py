#!/usr/bin/env python3

import pygame, time, math
pygame.init()

import config
screen = pygame.display.set_mode([config.WIDTH, config.HEIGHT], pygame.RESIZABLE)

from level import crawl_rooms, SPRITES
from util import SPRITE_SIZE, load_sprite, cut_sheet, draw_sprite

pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)

# Put loading screen stuff here
pygame.draw.rect(screen, (255, 255, 255), (0, 0, config.WIDTH, config.HEIGHT))
pygame.display.update()

PLAYER_TOP_SPRITE = cut_sheet(SPRITES, 0, 6, scale=4)
PLAYER_BOTTOM_SPRITE = cut_sheet(SPRITES, 0, 7, scale=4)

levels = crawl_rooms()

def set_level(pos):
  global current_level, neighbors
  current_level, neighbors = levels[pos] # Start in 0, 0

  for loc in [pos] + neighbors:
    level, _ = levels[loc]
    level.preload()

def get_tile(x, y):
  return current_level.grid[(int(player_pos['x']+x), int(player_pos['y']+y))]

tick = time.time()
lastTick = tick
running = True

set_level((0, 0))

player_pos = {
  'x': current_level.spawn.location[0],
  'y': current_level.spawn.location[1],
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

  vel_x, vel_y = 0, 0

  if get_tile(0, 1).is_air():
    vel_y = delta * 10

  if keys[pygame.K_a]:
    vel_x += -delta * 10

  if keys[pygame.K_d]:
    vel_x += delta * 10

  if keys[pygame.K_w]:
    vel_y -= delta * 10

  if keys[pygame.K_s]:
    vel_y += delta * 10

  if not get_tile(0, vel_y).is_air():
    vel_y = min(vel_y, player_pos['y'] - int(player_pos['y']))
  
  # TODO implement x+y collision
  # if not get_tile(0, vel_x).is_air():
  #   sign = math.copysign(1, vel_x)
  #   if vel_x > 0:
  #     print('not air', int(player_pos['x'] - 0.5) - player_pos['x'])
  #     vel_x = min(vel_x, int(player_pos['x'] - 0.5) - player_pos['x'])
  #   else:
  #     vel_x = max(vel_x, int(player_pos['x']) - player_pos['x'])

  player_pos['x'] += vel_x
  player_pos['y'] += vel_y


  player_x = int(player_pos['x'] * SPRITE_SIZE * 4)
  player_y = int(player_pos['y'] * SPRITE_SIZE * 4)

  x_off = -player_x + (config.WIDTH >> 1)
  y_off = -player_y + (config.HEIGHT >> 1)
 
  pygame.draw.rect(screen, (0, 0, 0), (0, 0, config.WIDTH, config.HEIGHT))
  current_level.render(screen, bg=True, mg=True, x_off=x_off, y_off=y_off)

  draw_sprite(screen, PLAYER_TOP_SPRITE, player_x + x_off, player_y - SPRITE_SIZE * 4 + y_off)
  draw_sprite(screen, PLAYER_BOTTOM_SPRITE, player_x + x_off, player_y + y_off)
  # tickGame(delta, keys)
  # drawGame()

  current_level.render(screen, fg=True, x_off=x_off, y_off=y_off)
  pygame.display.update()
