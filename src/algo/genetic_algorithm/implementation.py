from copy import deepcopy
import random
from typing import Iterator, cast

from algo.genetic_algorithm.primitive import (
  Chromosome,
  ChromosomeFactory,
  CrossOverStrategy,
  GeneticAlgorithm,
  MutationStrategy,
  PairPickingStrategy,
  Population,
  SelectionStrategy,
  TerminationStrategy,
)
from objects.state import State, StateFactory
from objects.vehicle import Vehicle


class StateChromosome(Chromosome):
  def __init__(self, state_factory: StateFactory, order: list[int], rotations: list[bool]):
    self.state_factory = state_factory
    self.order = order[:]
    self.rotations = rotations[:]
    self.state = self.decode()

  def decode(self) -> State:
    state = self.state_factory.create_state()
    vehicles = state.vehicles_outside[:]
    loaded_weight = 0
    for index in self.order:
      vehicle = vehicles[index]
      if self.rotations[index]:
        self._rotate(vehicle)
      if loaded_weight + vehicle.weight > state.ship.max_capacity:
        continue
      if self._place_vehicle(state, vehicle):
        state.vehicles_outside.remove(vehicle)
        loaded_weight += vehicle.weight
    return state

  def _rotate(self, vehicle: Vehicle) -> None:
    orientation = "vertical" if vehicle.orientation == "horizontal" else "horizontal"
    vehicle.set_orientation(orientation)

  def _place_vehicle(self, state: State, vehicle: Vehicle) -> bool:
    ship = state.ship
    for _ in range(2):
      for y in range(ship.rect.height):
        for x in range(ship.rect.width):
          if ship.vehicle_can_fit(vehicle, x, y):
            ship.move(vehicle, x, y)
            return True
      self._rotate(vehicle)
    return False

  def fitness(self) -> float:
    return self.state.get_objective()

  def clone(self) -> "StateChromosome":
    clone = object.__new__(StateChromosome)
    clone.state_factory = self.state_factory
    clone.order = self.order[:]
    clone.rotations = self.rotations[:]
    clone.state = deepcopy(self.state)
    return clone


class StateChromosomeFactory(ChromosomeFactory):
  def __init__(self, state_factory: StateFactory):
    super().__init__()
    self.state_factory = state_factory

  def randomized_chromosome(self) -> StateChromosome:
    order = list(range(len(self.state_factory.vehicles)))
    random.shuffle(order)
    return StateChromosome(self.state_factory, order, [bool(random.getrandbits(1)) for _ in order])


class MaxGenTermination(TerminationStrategy):
  def __init__(self, max_generation: int):
    if max_generation < 0:
      raise ValueError("Generations cannot be negative")
    self.max_generation = max_generation
    self.count = 0

  def can_terminate(self) -> bool:
    if self.count >= self.max_generation:
      return True
    self.count += 1
    return False


class RouletteWheelSelectionStrategy(SelectionStrategy):
  def pick(self, chromosomes: list[Chromosome]) -> Iterator[Chromosome]:
    weights = [max(0.0, item.fitness()) for item in chromosomes]
    yield from random.choices(chromosomes, weights=weights if any(weights) else None, k=len(chromosomes))


class RandomPairPickingStrategy(PairPickingStrategy):
  def _pairs_algo(self, chromosomes: list[Chromosome]) -> list[tuple[Chromosome, Chromosome]]:
    shuffled = chromosomes[:]
    random.shuffle(shuffled)
    return list(zip(shuffled[::2], shuffled[1::2]))


class OrderCrossOverStrategy(CrossOverStrategy):
  def _cross_algo(self, pair: tuple[Chromosome, Chromosome]) -> tuple[Chromosome, Chromosome]:
    first, second = cast(tuple[StateChromosome, StateChromosome], pair)
    size = len(first.order)
    if size < 2:
      return first.clone(), second.clone()
    start, stop = sorted(random.sample(range(size + 1), 2))

    def make_child(parent: StateChromosome, other: StateChromosome) -> StateChromosome:
      segment = parent.order[start:stop]
      remainder = [gene for gene in other.order if gene not in segment]
      order = remainder[:start] + segment + remainder[start:]
      rotations = [random.choice((parent.rotations[index], other.rotations[index])) for index in range(size)]
      return StateChromosome(parent.state_factory, order, rotations)

    return make_child(first, second), make_child(second, first)


class SwapMutationStrategy(MutationStrategy):
  def _mutate_algo(self, chromosome: Chromosome) -> None:
    state_chromosome = cast(StateChromosome, chromosome)
    if not state_chromosome.order:
      return
    if len(state_chromosome.order) >= 2:
      first, second = random.sample(range(len(state_chromosome.order)), 2)
      order = state_chromosome.order
      order[first], order[second] = order[second], order[first]
    index = random.randrange(len(state_chromosome.order))
    state_chromosome.rotations[index] = not state_chromosome.rotations[index]
    state_chromosome.state = state_chromosome.decode()


class GARunner:
  def __init__(self, state_factory: StateFactory, population_size: int = 16, generations: int = 100, crossover_rate: float = 0.85, mutation_rate: float = 0.25):
    factory = StateChromosomeFactory(state_factory)
    population = Population(population_size, factory)
    termination = MaxGenTermination(generations)
    crossover = OrderCrossOverStrategy(crossover_rate)
    selection = RouletteWheelSelectionStrategy()
    pairing = RandomPairPickingStrategy()
    mutation = SwapMutationStrategy(mutation_rate)
    self.genetic_algorithm = GeneticAlgorithm(population, termination, crossover, selection, pairing, mutation)

  @property
  def history(self) -> list[float]:
    return self.genetic_algorithm.history

  def run(self) -> State:
    return cast(StateChromosome, self.genetic_algorithm.run()).state
