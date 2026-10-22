import time
from copy import copy
from objects.state import State, StateFactory
from objects.vehicle import Vehicle
from algo.Steepest_Ascend_HC import SteepestAscentHillClimb
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


class RandomRestartHillClimb(_HillClimb):
  def __init__(
    self,
    state_factory: StateFactory,
    max_iterations: int = 1000,
    max_restarts: int = 10,
  ):
    super().__init__(state_factory, max_iterations)
    if max_restarts < 0:
      raise ValueError("Batas restart tidak boleh negatif")
    self.max_restarts = max_restarts
    self.restarts: int = 0
    self.iterations_per_restart: list[int] = []

  def visualize(self, title: str = "Random Restart Hill Climbing", save_dir: str | None = None) -> None:
    if self.final_state is None:
      raise RuntimeError("Jalankan run() terlebih dahulu sebelum visualize()")
    print(f"Banyak restart               : {self.restarts}")
    print(f"Banyak iterasi per restart   : {self.iterations_per_restart}")
    extra = {
      "Banyak restart": self.restarts,
      "Iterasi per restart": self.iterations_per_restart,
      "Max restarts": self.max_restarts,
    }
    visualize_hc_results(
      self.initial_state,
      self.final_state,
      self.history,
      title=title,
      duration=self.duration,
      save_dir=save_dir,
      extra_info=extra,
    )

  def run(self, initial_state: State | None = None) -> State:
    start_time = time.perf_counter()
    inner = SteepestAscentHillClimb(self.state_factory, self.max_iterations)

    current = initial_state if initial_state is not None else self.state_factory.create_random_state()
    self.initial_state = current
    best = inner.run(current)
    best_score = best.get_objective()
    self.history = list(inner.history)
    self.iterations_per_restart = [inner.iterations]
    self.restarts = 0

    for _ in range(self.max_restarts):
      self.restarts += 1
      start = self.state_factory.create_random_state()
      result = inner.run(start)
      self.history.extend(inner.history)
      self.iterations_per_restart.append(inner.iterations)

      score = result.get_objective()
      if score > best_score:
        best_score = score
        best = result

    self.iterations = sum(self.iterations_per_restart)
    self.final_state = best
    self.duration = time.perf_counter() - start_time
    return best
