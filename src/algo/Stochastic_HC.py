import random
import time
from copy import copy
from objects.state import State, StateFactory
from objects.vehicle import Vehicle
from visualizations.ship import visualize_hc_results


class _HillClimb:
  def __init__(self, state_factory: StateFactory, max_iterations: int = 1000):
    if max_iterations < 0:
      raise ValueError("Batas iterasi tidak boleh negatif")
    self.state_factory = state_factory
    self.max_iterations = max_iterations
    self.history: list[int] = []
    self.initial_state: State | None = None
    self.final_state: State | None = None
    self.duration: float = 0.0
    self.iterations: int = 0

  def visualize(self, title: str = "Hill Climbing", save_dir: str | None = None) -> None:
    if self.final_state is None:
      raise RuntimeError("Jalankan run() terlebih dahulu sebelum visualize()")
    visualize_hc_results(
      self.initial_state,
      self.final_state,
      self.history,
      title=title,
      duration=self.duration,
      save_dir=save_dir,
    )

  def _clone_vehicle(self, vehicle: Vehicle) -> Vehicle:
    new_vehicle = copy(vehicle)
    new_vehicle.rect = copy(vehicle.rect)
    return new_vehicle

  def _fast_clone_state(self, state: State) -> State:
    vehicle_map = {
      v.id: self._clone_vehicle(v)
      for v in state.ship.vehicles + state.vehicles_outside
    }

    new_ship = copy(state.ship)
    new_ship.rect = copy(state.ship.rect)
    new_ship.vehicles = [vehicle_map[v.id] for v in state.ship.vehicles]
    new_ship.slots = [row[:] for row in state.ship.slots]

    new_state = copy(state)
    new_state.ship = new_ship
    new_state.vehicles_outside = [vehicle_map[v.id] for v in state.vehicles_outside]
    return new_state

  def _iter_neighbors(self, state: State):
    vehicles = state.ship.vehicles + state.vehicles_outside

    for vehicle in vehicles:
      was_loaded = vehicle in state.ship.vehicles
      old_x, old_y = vehicle.rect.x, vehicle.rect.y
      old_orientation = vehicle.orientation

      if was_loaded:
        state.ship.remove(vehicle)
        state.vehicles_outside.append(vehicle)

        yield self._fast_clone_state(state)

        state.vehicles_outside.remove(vehicle)
        state.ship.move(vehicle, old_x, old_y)

      if was_loaded:
        state.ship.remove(vehicle)
        state.vehicles_outside.append(vehicle)

      loaded_weight = sum(item.weight for item in state.ship.vehicles)
      if loaded_weight + vehicle.weight > state.ship.max_capacity:
        if was_loaded:
          state.vehicles_outside.remove(vehicle)
          state.ship.move(vehicle, old_x, old_y)
        continue

      orientations = ("horizontal", "vertical")
      if vehicle.rect.width == vehicle.rect.height:
        orientations = (vehicle.orientation,)

      for orientation in orientations:
        vehicle.set_orientation(orientation)
        for y in range(state.ship.rect.height):
          for x in range(state.ship.rect.width):
            if was_loaded and (x, y) == (old_x, old_y) and orientation == old_orientation:
              continue
            if not state.ship.vehicle_can_fit(vehicle, x, y):
              continue

            state.vehicles_outside.remove(vehicle)
            state.ship.move(vehicle, x, y)

            yield self._fast_clone_state(state)

            state.ship.remove(vehicle)
            state.vehicles_outside.append(vehicle)

      vehicle.set_orientation(old_orientation)
      if was_loaded:
        state.vehicles_outside.remove(vehicle)
        state.ship.move(vehicle, old_x, old_y)


class StochasticHillClimb(_HillClimb):
  def visualize(self, title: str = "Stochastic Hill Climbing", save_dir: str | None = None) -> None:
    super().visualize(title=title, save_dir=save_dir)

  def run(self, initial_state: State | None = None) -> State:
    start_time = time.perf_counter()
    current = initial_state or self.state_factory.create_state()
    self.initial_state = current
    self.history = [current.get_objective()]
    self.iterations = 0

    for _ in range(self.max_iterations):
      current_score = current.get_objective()
      better_neighbors = [
        neighbor for neighbor in self._iter_neighbors(current)
        if neighbor.get_objective() > current_score
      ]

      if not better_neighbors:
        break

      current = random.choice(better_neighbors)
      self.history.append(current.get_objective())
      self.iterations += 1

    self.final_state = current
    self.duration = time.perf_counter() - start_time
    return current
