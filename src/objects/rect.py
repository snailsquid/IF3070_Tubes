class Rect:
  def __init__(self, width: int, height: int):
    if width <= 0 or height <= 0 : raise ValueError()
    self.width = width
    self.height = height
    self.x = -1
    self.y = -1
  def set_position(self, x: int, y: int):
    self.x = x
    self.y = y
