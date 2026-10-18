from copy import deepcopy
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
  vehicles_outside: list[VehicleData]


class State:
  def __init__(self, ship: Ship, vehicles_outside: list[Vehicle]):
    self.ship = ship
    self.vehicles_outside = vehicles_outside

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
      },
      "vehicles_outside": [
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
        for vehicle in self.vehicles_outside
      ]
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
      vehicle = Vehicle(item["id"], item["width"], item["height"], item["weight"], item["shipping_fee"], item["eta"])
      vehicle.orientation = item["orientation"]
      ship.move(vehicle, item["x"], item["y"])
    vehicles_outside_data = data["vehicles_outside"]
    vehicles_outside: list[Vehicle] = []
    for item in vehicles_outside_data:
      vehicle = Vehicle(item["id"], item["width"], item["height"], item["weight"], item["shipping_fee"], item["eta"])
      vehicles_outside.append(vehicle)

    return cls(ship, vehicles_outside)

  def get_objective(self) -> int:
    return sum(vehicle.shipping_fee for vehicle in self.ship.vehicles)

class StateFactory:
  def __init__(self, ship: Ship, vehicles: list[Vehicle]) -> None:
    self.ship = Ship.new_from_config(ship)
    self.vehicles = deepcopy(vehicles)

  def create_state(self) -> State:
    return State(Ship.new_from_config(self.ship), deepcopy(self.vehicles))
