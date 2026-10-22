import random

from objects.rect import Rect
from objects.vehicle import Vehicle

class Ship:
  def __init__(self, width: int, height: int, max_capacity: int):
    self.rect = Rect(width, height)
    self.vehicles: list[Vehicle] = []
    self.slots: list[list[bool]] = [[False for _ in range(width)] for _ in range(height)]
    self.max_capacity = max_capacity

  @property
  def total_weight(self) -> int:
    return sum(v.weight for v in self.vehicles)

  def can_fit_weight(self, vehicle: Vehicle) -> bool:
    return self.total_weight + vehicle.weight <= self.max_capacity

  def try_place_randomly(self, vehicle: Vehicle) -> bool:
    max_x = self.rect.width - vehicle.rect.width
    max_y = self.rect.height - vehicle.rect.height
    if max_x < 0 or max_y < 0:
      return False

    valid_positions: list[tuple[int, int]] = []
    for y in range(max_y + 1):
      for x in range(max_x + 1):
        if self.vehicle_can_fit(vehicle, x, y):
          valid_positions.append((x, y))

    if not valid_positions:
      return False

    x, y = random.choice(valid_positions)
    self.move(vehicle, x, y)
    return True

  @classmethod
  def new_from_config(cls, ship: "Ship") -> "Ship":
    return cls(ship.rect.width, ship.rect.height, ship.max_capacity)

  def slot_is_occupied(self, x: int, y: int) -> bool:
    if not (0 <= x < self.rect.width and 0 <= y < self.rect.height):
      raise IndexError("Slot is outside the ship")
    return self.slots[y][x]

  def vehicle_can_fit(self, vehicle: Vehicle, x: int | None = None, y: int | None = None) -> bool:
    x = vehicle.rect.x if x is None else x
    y = vehicle.rect.y if y is None else y
    if x < 0 or y < 0 or x + vehicle.rect.width > self.rect.width or y + vehicle.rect.height > self.rect.height:
      return False
    for i in range(vehicle.rect.height):
      for j in range(vehicle.rect.width):
        if not self.slot_is_occupied(x + j, y + i):
          continue
        in_current_footprint = vehicle.rect.x <= x + j < vehicle.rect.x + vehicle.rect.width and vehicle.rect.y <= y + i < vehicle.rect.y + vehicle.rect.height
        if vehicle not in self.vehicles or not in_current_footprint:
          return False
    return True

  def move(self, vehicle: Vehicle, x: int | None = None, y: int | None = None):
    x = vehicle.rect.x if x is None else x
    y = vehicle.rect.y if y is None else y
    if not self.vehicle_can_fit(vehicle, x, y):
      raise ValueError("Vehicle cannot fit")
    if vehicle in self.vehicles:
      self._mark(vehicle, False)
    else:
      self.vehicles.append(vehicle)
    vehicle.rect.set_position(x, y)
    self._mark(vehicle, True)

  def orient(self, vehicle: Vehicle, orientation: str):
    if orientation not in ("horizontal", "vertical"):
      raise ValueError("Orientation must be horizontal or vertical")
    if orientation == vehicle.orientation:
      return
    if vehicle not in self.vehicles:
      vehicle.set_orientation(orientation)
      return
    x, y = vehicle.rect.x, vehicle.rect.y
    old_width, old_height = vehicle.rect.width, vehicle.rect.height
    if x + old_height > self.rect.width or y + old_width > self.rect.height:
      raise ValueError("Vehicle cannot fit")
    for row in range(y, y + old_width):
      for col in range(x, x + old_height):
        in_old_footprint = x <= col < x + old_width and y <= row < y + old_height
        if self.slot_is_occupied(col, row) and not in_old_footprint:
          raise ValueError("Vehicle cannot fit")
    self._mark(vehicle, False)
    vehicle.set_orientation(orientation)
    self._mark(vehicle, True)

  def _mark(self, vehicle: Vehicle, occupied: bool):
    for y in range(vehicle.rect.y, vehicle.rect.y + vehicle.rect.height):
      for x in range(vehicle.rect.x, vehicle.rect.x + vehicle.rect.width):
        self.slots[y][x] = occupied

  def remove(self, vehicle: Vehicle):
    if vehicle not in self.vehicles:
      raise ValueError("Vehicle not in ship")
    self._mark(vehicle, False)
    self.vehicles.remove(vehicle)
    vehicle.remove_position()

  def replace(self, old_vehicle: Vehicle, new_vehicle: Vehicle):
    if old_vehicle not in self.vehicles:
      raise ValueError("Vehicle not in ship")
    if new_vehicle in self.vehicles:
      raise ValueError("Replacement vehicle is already in ship")
    x, y = old_vehicle.rect.x, old_vehicle.rect.y
    if x + new_vehicle.rect.width > self.rect.width or y + new_vehicle.rect.height > self.rect.height:
      raise ValueError("Vehicle cannot fit")
    for row in range(y, y + new_vehicle.rect.height):
      for col in range(x, x + new_vehicle.rect.width):
        in_old_footprint = col < x + old_vehicle.rect.width and row < y + old_vehicle.rect.height
        if self.slot_is_occupied(col, row) and not in_old_footprint:
          raise ValueError("Vehicle cannot fit")
    index = self.vehicles.index(old_vehicle)
    self._mark(old_vehicle, False)
    old_vehicle.remove_position()
    new_vehicle.rect.set_position(x, y)
    self.vehicles[index] = new_vehicle
    self._mark(new_vehicle, True)
