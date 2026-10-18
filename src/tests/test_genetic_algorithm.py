import random
import unittest

from algo.genetic_algorithm.implementation import (
  GARunner,
  OrderCrossOverStrategy,
  StateChromosome,
  StateChromosomeFactory,
  SwapMutationStrategy,
)
from objects.ship import Ship
from objects.state import StateFactory
from objects.vehicle import VehicleBuilder


class GeneticAlgorithmTests(unittest.TestCase):
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

  def test_evolution_keeps_valid_layouts_and_best_fitness(self):
    runner = GARunner(self.factory, population_size=12, generations=15)
    state = runner.run()
    self.assertEqual(len(runner.history), 16)
    self.assertEqual(runner.history, sorted(runner.history))
    self.assertEqual(state.get_objective(), runner.history[-1])
    self.assert_valid(state)
    for chromosome in runner.genetic_algorithm.population.chromosomes:
      assert isinstance(chromosome, StateChromosome)
      self.assert_valid(chromosome.state)
    self.assertTrue(all(v.rect.x == -1 for v in self.vehicles))

  def test_operators_preserve_genes_and_do_not_change_parents(self):
    factory = StateChromosomeFactory(self.factory)
    parents = factory.randomized_chromosome(), factory.randomized_chromosome()
    orders = [p.order[:] for p in parents]
    for _ in range(20):
      children = OrderCrossOverStrategy(1).cross(parents)
      for child in children:
        assert isinstance(child, StateChromosome)
        SwapMutationStrategy(1).mutate(child)
        self.assertEqual(sorted(child.order), list(range(len(self.vehicles))))
        self.assert_valid(child.state)
    self.assertEqual([p.order for p in parents], orders)

  def test_empty_input_zero_generations_and_validation(self):
    runner = GARunner(StateFactory(Ship(2, 2, 0), []), population_size=2, generations=0)
    self.assertEqual(runner.run().get_objective(), 0)
    self.assertEqual(runner.history, [0])
    for size in (0, 1, 3):
      with self.assertRaises(ValueError):
        GARunner(self.factory, population_size=size)
    with self.assertRaises(ValueError):
      GARunner(self.factory, generations=-1)

  def test_factory_states_are_independent(self):
    first, second = self.factory.create_state(), self.factory.create_state()
    vehicle = first.vehicles_outside.pop()
    first.ship.move(vehicle, 0, 0)
    self.assertTrue(all(v.rect.x == -1 for v in second.vehicles_outside))


if __name__ == '__main__':
  unittest.main()
