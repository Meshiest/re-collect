import pygame

from rect_base import RectBase

class Platform(RectBase):
  def __init__(self, **kwargs):
    super.__init__(kwargs)

  def tick(self, **kwargs):
    super.tick(kwargs)

  def draw(self, **kwargs):
    super.draw(kwargs)
