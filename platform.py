import pygame

from rect_base import RectBase

class Platform(RectBase):
  def __init__(self, *args):
    super().__init__(*args)

  def draw(self, scr, *args):
    super().draw(scr, *args)
    pygame.draw.rect(scr, self.color, (self.x, self.y, self.w, self.h))
