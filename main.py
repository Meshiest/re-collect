#!/usr/bin/env python3

import pygame, time

import config

from level import crawl_rooms

pygame.init()
pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)

screen = pygame.display.set_mode([config.WIDTH, config.HEIGHT], pygame.RESIZABLE)

# Put loading screen stuff here
pygame.draw.rect(screen, (255, 255, 255), (0, 0, config.WIDTH, config.HEIGHT))
pygame.display.update()

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
print(current_level)

while running:
  lastTick, tick = tick, time.time()
  delta = tick - lastTick

  keys = pygame.key.get_pressed()

  if keys[pygame.K_ESCAPE]:
    running = False
    break

  keyPressed = {}

  pygame.draw.rect(screen, (0, 0, 0), (0, 0, config.WIDTH, config.HEIGHT))

  for event in pygame.event.get():
    if event.type == pygame.QUIT:
      running = False

    if event.type == pygame.VIDEORESIZE:
      config.WIDTH, config.HEIGHT = event.dict['size']
      screen = pygame.display.set_mode((config.WIDTH, config.HEIGHT), pygame.RESIZABLE)

    if event.type == pygame.KEYDOWN: # assign the key if it's down
      keyPressed[event.dict['key']] = True

  # tickGame(delta, keys)
  # drawGame()

  pygame.display.update()
