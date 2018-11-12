#!/usr/bin/env python3

import pygame, time
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

tick = time.time()
lastTick = tick
running = True

set_level((0, 0))

playerPos = {
  'x': current_level.spawn.location[0] * SPRITE_SIZE * 4,
  'y': current_level.spawn.location[1] * SPRITE_SIZE * 4,
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

  if(keys[pygame.K_a]):
    playerPos['x'] -= delta * 300

  if(keys[pygame.K_d]):
    playerPos['x'] += delta * 300

  if(keys[pygame.K_w]):
    playerPos['y'] -= delta * 300

  if(keys[pygame.K_s]):
    playerPos['y'] += delta * 300

  x_off = -int(playerPos['x']) + (config.WIDTH >> 1)
  y_off = -int(playerPos['y']) + (config.HEIGHT >> 1)
 
  pygame.draw.rect(screen, (0, 0, 0), (0, 0, config.WIDTH, config.HEIGHT))
  current_level.render(screen, bg=True, mg=True, x_off=x_off, y_off=y_off)

  draw_sprite(screen, PLAYER_TOP_SPRITE, int(playerPos['x']) + x_off, int(playerPos['y'] - SPRITE_SIZE * 4) + y_off)
  draw_sprite(screen, PLAYER_BOTTOM_SPRITE, int(playerPos['x']) + x_off, int(playerPos['y']) + y_off)
  # tickGame(delta, keys)
  # drawGame()

  current_level.render(screen, fg=True, x_off=x_off, y_off=y_off)
  pygame.display.update()
