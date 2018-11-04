import pygame

from rect_base import RectBase

class Player(RectBase):
  def __init__(self, *args):
    super().__init__(*args)
    self.items = []
    self.action = None
    self.powerup_start = None
    self.v = 5
    self.m = 2

  def tick(self, delta, collidables, scr):
    for collidable in collidables:
      if self.y > (collidable.y + collidable.h):
        pass
      elif self.collide((self.vx * delta), (self.vy * delta), collidable):
        return
    if self.boundaries(self.x + (self.vx * delta), self.y + (self.vx * delta), scr):
      super().tick(delta)    

  def move(self, deltax, deltay):
    self.x += deltax
    self.y += deltay

  def draw(self, scr, *args):
    pygame.draw.rect(scr, self.color, (self.x, self.y, self.w, self.h))

  def collide(self, deltax, deltay, other_rect):
   player = pygame.Rect(self.x+deltax, self.y+deltay, 50, 10)
   other = pygame.Rect(other_rect.x, other_rect.y, other_rect.w, other_rect.h)
   if player.colliderect(other):
     return True
   return False

  def boundaries(self, x, y, scr):
    rect = pygame.Rect(x, y, 50, 10)
    screen = scr.get_rect()
    return screen.contains(rect)
 
  def interact(self, interactable):
    pass

  def interactable_portal(self, x, y):
    pass

  def portal(self):
    pass

  def jump(self, delta):
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
