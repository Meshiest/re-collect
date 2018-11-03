import pygame

from rect_base import RectBase

class Player(RectBase):
  def __init__(self, **kwargs):
    super.__init__(kwargs)
    self.items = []
    self.action = None
    self.powerup_start = None

  def tick(self, **kwargs):
    super.tick(kwargs)

  def draw(self, **kwargs):
    super.draw(kwargs)

  def interact(self, interactable):
    pass

  def interactable_portal(self, x, y):
    pass

  def portal(self):
    pass

  def jump(self):
    pass

  def dash(self):
    pass

  def inverse_gravity(self):
    pass

  def eat_mushroom(self, mushroom_type):
    for item_index in range(len(self.items)):
      item = self.items[item_index]
      if item.type == mushroom_type:
        item.respawn()
        self.action = item.action
        del self.items[item_index]
        self.powerup_start = time.time()
        if self.action == 3: # flip gravity happpens
          pass
        return

  def action(self):
    if self.action == 0:
      return
    elif self.action == 1: # jump
      pass
    elif self.action == 2: #dash
     pass
