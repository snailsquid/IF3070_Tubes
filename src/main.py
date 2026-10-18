from algo.genetic_algorithm.implementation import GARunner
from objects.ship import Ship
from objects.vehicle import Vehicle, VehicleBuilder
from objects.state import StateFactory
from visualizations.ship import visualize_state


def init_ship() -> Ship:
  return Ship(5, 6, 4500)


def init_vehicles() -> list[Vehicle]:
  builder = VehicleBuilder()
  return [
    builder.car(),
    builder.car(),
    builder.car(),
    builder.truck(),
    builder.truck(),
    builder.truck(),
    builder.truck(),
    builder.motorcycle(),
    builder.motorcycle(),
    builder.motorcycle(),
    builder.quadcopter(),
    builder.quadcopter(),
    builder.quadcopter(),
  ]


def main() -> None:
  ship = init_ship()
  vehicles = init_vehicles()
  state_factory = StateFactory(ship, vehicles)
  algorithm = GARunner(state_factory)
  state = algorithm.run()
  visualize_state(state)


if __name__ == "__main__":
  main()
