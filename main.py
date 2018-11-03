#!/usr/bin/env python3

import pygame, time

import config

pygame.init()
pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)

screen = pygame.display.set_mode([config.WIDTH, config.HEIGHT], pygame.RESIZABLE)

tick = time.time()
lastTick = tick
running = True

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

  # tickGame(delta, keys)
  # drawGame()

  pygame.display.update()
