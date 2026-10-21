import random
import unittest

from algo.simulated_annealing import SimulatedAnnealing
from objects.ship import Ship
from objects.state import StateFactory
from objects.vehicle import VehicleBuilder


class SimulatedAnnealingTests(unittest.TestCase):
  def setUp(self):
    random.seed(7)
    builder = VehicleBuilder()
    self.vehicles = [builder.car() for _ in range(4)] + [builder.truck() for _ in range(4)]
    self.vehicles += [builder.motorcycle() for _ in range(4)] + [builder.quadcopter() for _ in range(4)]
    self.factory = StateFactory(Ship(5, 6, 3500), self.vehicles)

  def assert_valid(self, state):
    occupied = set()
    self.assertLessEqual(sum(v.weight for v in state.ship.vehicles), state.ship.max_capacity)
    all_vehicles = state.ship.vehicles + state.vehicles_outside
    self.assertCountEqual([v.id for v in all_vehicles], [v.id for v in self.vehicles])
    for vehicle in state.ship.vehicles:
      for y in range(vehicle.rect.y, vehicle.rect.y + vehicle.rect.height):
        for x in range(vehicle.rect.x, vehicle.rect.x + vehicle.rect.width):
          self.assertTrue(0 <= x < state.ship.rect.width)
          self.assertTrue(0 <= y < state.ship.rect.height)
          self.assertNotIn((x, y), occupied)
          occupied.add((x, y))
    self.assertEqual(len(occupied), sum(sum(row) for row in state.ship.slots))

  def test_simulated_annealing_produces_valid_state(self):
    sa = SimulatedAnnealing(initial_temperature=100.0, cooling_rate=0.95, min_temperature=1.0)
    state = sa.run(self.factory)
    self.assert_valid(state)
    self.assertGreater(state.get_objective(), 0)
    self.assertTrue(len(sa.history_objective) > 0)

  def test_simulated_annealing_with_factory(self):
    sa = SimulatedAnnealing(self.factory, initial_temperature=100.0, cooling_rate=0.95, min_temperature=1.0)
    state = sa.run()
    self.assert_valid(state)
    self.assertEqual(len(sa.history), len(sa.history_objective))

  def test_empty_ship_or_vehicles(self):
    sa = SimulatedAnnealing(StateFactory(Ship(2, 2, 0), []))
    state = sa.run()
    self.assertEqual(state.get_objective(), 0)

  def test_factory_states_are_independent(self):
    first, second = self.factory.create_state(), self.factory.create_state()
    vehicle = first.vehicles_outside.pop()
    first.ship.move(vehicle, 0, 0)
    self.assertTrue(all(v.rect.x == -1 for v in second.vehicles_outside))

if __name__ == "__main__":
  unittest.main()
