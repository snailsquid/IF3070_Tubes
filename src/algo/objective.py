from objects.state import State

def objective(state: State) -> int:
  return sum(vehicle.shipping_fee for vehicle in state.ship.vehicles)