from algo.simulated_annealing import SimulatedAnnealing
from objects.ship import Ship
from objects.state import StateFactory
from objects.vehicle import Vehicle, VehicleBuilder
from visualizations.ship import visualize_sa_results


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
  algorithm = SimulatedAnnealing(state_factory)
  state = algorithm.run()
  state.save_yaml("../output/simulated_annealing.yaml")
  visualize_sa_results(
    initial_state=algorithm.initial_state,
    final_state=state,
    history=algorithm.history,
    history_prob=algorithm.history_probability,
  )


if __name__ == "__main__":
  main()