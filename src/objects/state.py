from pathlib import Path
from typing import TypedDict, cast

import yaml

from objects.ship import Ship
from objects.vehicle import Vehicle


class VehicleData(TypedDict):
  id: str
  width: int
  height: int
  x: int
  y: int
  orientation: str
  weight: int
  shipping_fee: int
  eta: int


class ShipData(TypedDict):
  width: int
  height: int
  max_capacity: int
  vehicles: list[VehicleData]


class StateData(TypedDict):
  ship: ShipData


class State:
  def __init__(self, ship: Ship):
    self.ship = ship

  def save_yaml(self, path: str | Path) -> None:
    data: StateData = {
      "ship": {
        "width": self.ship.rect.width,
        "height": self.ship.rect.height,
        "max_capacity": self.ship.max_capacity,
        "vehicles": [
          {
            "id": vehicle.id,
            "width": vehicle.rect.width,
            "height": vehicle.rect.height,
            "x": vehicle.rect.x,
            "y": vehicle.rect.y,
            "orientation": vehicle.orientation,
            "weight": vehicle.weight,
            "shipping_fee": vehicle.shipping_fee,
            "eta": vehicle.eta,
          }
          for vehicle in self.ship.vehicles
        ],
      }
    }
    with Path(path).open("w", encoding="utf-8") as file:
      yaml.safe_dump(data, file, sort_keys=False)

  @classmethod
  def load_yaml(cls, path: str | Path) -> "State":
    with Path(path).open("r", encoding="utf-8") as file:
      data = cast(StateData, yaml.safe_load(file))
    ship_data = data["ship"]
    ship = Ship(ship_data["width"], ship_data["height"], ship_data["max_capacity"])
    for item in ship_data["vehicles"]:
      vehicle = Vehicle(
        item["id"], item["width"], item["height"], item["weight"],
        item["shipping_fee"], item["eta"],
      )
      vehicle.orientation = item["orientation"]
      ship.move(vehicle, item["x"], item["y"])
    return cls(ship)
