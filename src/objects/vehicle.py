from objects.rect import Rect

TRUCK_ID = "truck"
MOTORCYCLE_ID = "motorcycle"
CAR_ID = "car"
QUADCOPTER_ID = "quadcopter"

class Vehicle:
  def __init__(self, id: str, width : int, height : int, weight : int, shipping_fee: int, eta: int):
    self.id = id
    self.rect = Rect(width, height)
    self.orientation = "horizontal" if width >= height else "vertical"
    self.remove_position()
    self.weight = weight
    self.shipping_fee = shipping_fee
    self.eta = eta
  def remove_position(self):
    self.rect.set_position(-1, -1)
  def set_orientation(self, orientation: str):
    if orientation not in ("horizontal", "vertical"):
      raise ValueError("Orientation must be horizontal or vertical")
    if orientation != self.orientation:
      self.rect.width, self.rect.height = self.rect.height, self.rect.width
      self.orientation = orientation
class VehicleBuilder:
  counter : dict[str, int] = {}
  def truck(self) -> Vehicle:
    self.counter[TRUCK_ID] = self.counter.get(TRUCK_ID, 0) + 1
    return Vehicle(id=f"{TRUCK_ID}-{self.counter[TRUCK_ID]}", width=1, height=3, weight=1000, shipping_fee=500, eta=2)
  def motorcycle(self) -> Vehicle:
    self.counter[MOTORCYCLE_ID] = self.counter.get(MOTORCYCLE_ID, 0) + 1
    return Vehicle(id=f"{MOTORCYCLE_ID}-{self.counter[MOTORCYCLE_ID]}", width=1, height=1, weight=20, shipping_fee=50, eta=2)
  def car(self) -> Vehicle:
    self.counter[CAR_ID] = self.counter.get(CAR_ID, 0) + 1
    return Vehicle(id=f"{CAR_ID}-{self.counter[CAR_ID]}", width=1, height=2, weight=500, shipping_fee=100, eta=3)
  def quadcopter(self) -> Vehicle:
    self.counter[QUADCOPTER_ID] = self.counter.get(QUADCOPTER_ID, 0) + 1
    return Vehicle(id=f"{QUADCOPTER_ID}-{self.counter[QUADCOPTER_ID]}", width=2, height=2, weight=5, shipping_fee=200, eta=1)