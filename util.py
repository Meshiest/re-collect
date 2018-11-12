import pygame, os

from config import SPRITE_SIZE

# Load an image from provided path
def load_sprite(path):
  if not path or len(path) == 0:
    return None
  
  # Return none if the file does not exist
  if not (os.path.exists(path) and os.path.isfile(path)):
    return None

  # Return pygame loading the image with proper transparency
  return pygame.image.load(os.path.abspath(path)).convert_alpha()

# Cut a sprite out of a sheet
def cut_sheet(src, x, y, size=SPRITE_SIZE):
  x *= size
  y *= size
  surface = pygame.Surface((size, size), pygame.SRCALPHA, 32).convert_alpha()
  surface.blit(src, surface.get_rect(), (x, y, x + size, y + size))
  return surface

def level_surface(width, height):
  return pygame.Surface((width * SPRITE_SIZE, height * SPRITE_SIZE), pygame.SRCALPHA, 32).convert_alpha()

# Draws a sprite on a surface at position x, y
def draw_sprite(src, sprite, x, y, scale=False, rotate=0, flip_x=False, flip_y=False, size=SPRITE_SIZE):
  if scale:
    x *= size
    y *= size

  if flip_x or flip_y:
    sprite = pygame.transform.flip(sprite, flip_x, flip_y)

  if rotate != 0:
    sprite = pygame.transform.rotate(
      sprite,
      theta / math.pi * 180
    )

  src.blit(sprite, (x, y, x + size, y + size))
