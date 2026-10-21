import math
import random
import time
from copy import deepcopy

from algo.objective import objective
from objects.ship import Ship
from objects.state import State, StateFactory
from objects.vehicle import Vehicle


def create_random_state(factory: StateFactory) -> State:
  return factory.create_random_state()


def _swap(ship: Ship, outside: list[Vehicle]) -> None:
  if outside and (len(ship.vehicles) < 2 or random.random() < 0.5):
    v_in, v_out = random.choice(ship.vehicles), random.choice(outside)
    if ship.total_weight - v_in.weight + v_out.weight <= ship.max_capacity:
      try:
        ship.replace(v_in, v_out)
        outside.remove(v_out)
        outside.append(v_in)
      except ValueError:
        orig_x, orig_y = v_in.rect.x, v_in.rect.y
        ship.remove(v_in)
        if ship.try_place_randomly(v_out):
          outside.remove(v_out)
          outside.append(v_in)
        else:
          ship.move(v_in, orig_x, orig_y)
  else:
    v1, v2 = random.sample(ship.vehicles, 2)
    x1, y1, x2, y2 = v1.rect.x, v1.rect.y, v2.rect.x, v2.rect.y
    ship.remove(v1)
    ship.remove(v2)
    try:
      ship.move(v2, x1, y1)
      ship.move(v1, x2, y2)
    except ValueError:
      if v2 in ship.vehicles:
        ship.remove(v2)
      ship.move(v1, x1, y1)
      ship.move(v2, x2, y2)


def _move_random(ship: Ship) -> None:
  v = random.choice(ship.vehicles)
  orig_x, orig_y = v.rect.x, v.rect.y
  ship.remove(v)
  if not ship.try_place_randomly(v):
    ship.move(v, orig_x, orig_y)


def _orient_random(ship: Ship) -> None:
  v = random.choice(ship.vehicles)
  new_ori = "vertical" if v.orientation == "horizontal" else "horizontal"
  try:
    ship.orient(v, new_ori)
  except ValueError:
    pass


def _generate_neighbor(state: State) -> State:
  neighbor = deepcopy(state)
  ship, outside = neighbor.ship, neighbor.vehicles_outside
  if not ship.vehicles and not outside:
    return neighbor

  move = random.choice(["swap", "move", "orient"])

  if move == "swap" and (len(ship.vehicles) >= 2 or (ship.vehicles and outside)):
    _swap(ship, outside)
  elif move == "move" and ship.vehicles:
    _move_random(ship)
  elif move == "orient" and ship.vehicles:
    _orient_random(ship)

  return neighbor


def _acceptance_probability(delta: float, temperature: float) -> float:
  return 1.0 if delta > 0 else math.exp(delta / temperature)


class SimulatedAnnealing:
  def __init__(
    self,
    state_factory: StateFactory | None = None,
    initial_temperature: float = 1000.0,
    cooling_rate: float = 0.995,
    min_temperature: float = 0.1,
  ) -> None:
    self.state_factory = state_factory
    self.initial_temperature = initial_temperature
    self.cooling_rate = cooling_rate
    self.min_temperature = min_temperature

    self.initial_state: State | None = None
    self.history: list[float] = []
    self.history_probability: list[float] = []
    self.stuck_count = 0
    self.duration = 0.0
    self.iterations = 0

  @property
  def history_objective(self) -> list[float]:
    return self.history

  def run(self, factory: StateFactory | None = None) -> State:
    target_factory = factory or self.state_factory
    if target_factory is None:
      raise ValueError("StateFactory diperlukan.")

    self.initial_state = target_factory.create_random_state()
    current = deepcopy(self.initial_state)
    best = deepcopy(current)
    temperature = self.initial_temperature

    current_val, best_val = objective(current), objective(best)
    self.history = [current_val]
    self.history_probability = [1.0]
    self.stuck_count = 0

    iterations = 0
    start_time = time.perf_counter()
    while temperature > self.min_temperature:
      iterations += 1
      neighbor = _generate_neighbor(current)
      neighbor_val = objective(neighbor)
      delta = neighbor_val - current_val

      prob = _acceptance_probability(delta, temperature)
      if delta > 0 or random.random() < prob:
        current, current_val = neighbor, neighbor_val
        if current_val > best_val:
          best, best_val = deepcopy(current), current_val
      else:
        self.stuck_count += 1

      self.history.append(current_val)
      self.history_probability.append(prob)
      temperature *= self.cooling_rate

    self.iterations = iterations
    self.duration = time.perf_counter() - start_time
    return best