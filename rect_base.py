import math
import pygame

class RectBase:
  def __init__(self, x, y, vx, vy):
    self.x = x
    self.y = y
    self.vx = vx
    self.vy = vy
    self.dir = -math.copysign(1, vx)
    self.theta = -math.pi/2


def tick(self, delta):
  self.x += self.vx * delta
  self.y += self.vy * delta
  self.vx *= (1-delta/2)
  self.vy += 100 * delta
  self.theta += math.pi*delta*self.dir
  if self.theta < -math.pi and self.dir == 1:
      self.dir = -1
  elif self.theta > 0 and self.dir == -1:
  self.dir = 1

def draw(self, scr, img):
  offX = math.cos(self.theta) * 20
  offY = -math.cos(self.theta) * 10
  scr.pygame.Surface.blit(img, (self.x+offX, self.y+offY))


