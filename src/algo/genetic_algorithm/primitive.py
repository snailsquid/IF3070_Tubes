from abc import ABC, abstractmethod
from copy import deepcopy
from enum import Enum
import random
from typing import Iterator


class Chromosome(ABC):
  @abstractmethod
  def fitness(self) -> float:
    pass

  def clone(self) -> "Chromosome":
    return deepcopy(self)


class ChromosomeFactoryStrategy(Enum):
  RANDOM = 1


class ChromosomeFactory(ABC):
  def __init__(self, strategy: ChromosomeFactoryStrategy = ChromosomeFactoryStrategy.RANDOM):
    self.strategy = strategy

  def create_chromosome(self) -> Chromosome:
    return self.randomized_chromosome()

  @abstractmethod
  def randomized_chromosome(self) -> Chromosome:
    pass


class TerminationStrategy(ABC):
  @abstractmethod
  def can_terminate(self) -> bool:
    pass


class Population:
  def __init__(self, size: int, chromosome_factory: ChromosomeFactory):
    if size < 2 or size % 2:
      raise ValueError("Population size must be even and at least two")
    self.size = size
    self.chromosomes = [chromosome_factory.create_chromosome() for _ in range(size)]


class SelectionStrategy(ABC):
  @abstractmethod
  def pick(self, chromosomes: list[Chromosome]) -> Iterator[Chromosome]:
    pass


class CrossOverStrategy(ABC):
  def __init__(self, probability: float):
    if not 0 <= probability <= 1:
      raise ValueError("Crossover probability must be between zero and one")
    self.probability = probability

  def cross(self, pair: tuple[Chromosome, Chromosome]) -> tuple[Chromosome, Chromosome]:
    if random.random() < self.probability:
      return self._cross_algo(pair)
    return pair[0].clone(), pair[1].clone()

  @abstractmethod
  def _cross_algo(self, pair: tuple[Chromosome, Chromosome]) -> tuple[Chromosome, Chromosome]:
    pass


class MutationStrategy(ABC):
  def __init__(self, probability: float):
    if not 0 <= probability <= 1:
      raise ValueError("Mutation probability must be between zero and one")
    self.probability = probability

  def mutate(self, chromosome: Chromosome) -> None:
    if random.random() < self.probability:
      self._mutate_algo(chromosome)

  @abstractmethod
  def _mutate_algo(self, chromosome: Chromosome) -> None:
    pass


class PairPickingStrategy(ABC):
  def create_pairs(self, chromosomes: list[Chromosome]) -> list[tuple[Chromosome, Chromosome]]:
    if len(chromosomes) % 2:
      raise ValueError("Pairing requires an even population")
    pairs = self._pairs_algo(chromosomes)
    if len(pairs) * 2 != len(chromosomes):
      raise ValueError("Pairing must preserve population size")
    return pairs

  @abstractmethod
  def _pairs_algo(self, chromosomes: list[Chromosome]) -> list[tuple[Chromosome, Chromosome]]:
    pass


class GeneticAlgorithm:
  def __init__(self, population: Population, termination_strategy: TerminationStrategy, cross_over_strategy: CrossOverStrategy, selection_strategy: SelectionStrategy, pair_picking_strategy: PairPickingStrategy, mutation_strategy: MutationStrategy):
    self.population = population
    self.termination_strategy = termination_strategy
    self.cross_over_strategy = cross_over_strategy
    self.selection_strategy = selection_strategy
    self.pair_picking_strategy = pair_picking_strategy
    self.mutation_strategy = mutation_strategy
    self.history = [self.best().fitness()]

  def best(self) -> Chromosome:
    return max(self.population.chromosomes, key=lambda item: item.fitness())

  def run(self) -> Chromosome:
    while not self.termination_check():
      self.step()
    return self.best().clone()

  def termination_check(self) -> bool:
    return self.termination_strategy.can_terminate()

  def step(self) -> None:
    elite = self.best().clone()
    self.select()
    self.cross_over()
    self.mutate()
    chromosomes = self.population.chromosomes
    worst_index = min(range(len(chromosomes)), key=lambda index: chromosomes[index].fitness())
    chromosomes[worst_index] = elite
    self.history.append(self.best().fitness())

  def select(self) -> None:
    selected = list(self.selection_strategy.pick(self.population.chromosomes))
    if len(selected) != self.population.size:
      raise ValueError("Selection must preserve population size")
    self.population.chromosomes = [item.clone() for item in selected]

  def mutate(self) -> None:
    for chromosome in self.population.chromosomes:
      self.mutation_strategy.mutate(chromosome)

  def create_pairs(self) -> list[tuple[Chromosome, Chromosome]]:
    return self.pair_picking_strategy.create_pairs(self.population.chromosomes)

  def cross_over(self) -> None:
    children = []
    for pair in self.create_pairs():
      children.extend(self.cross_over_strategy.cross(pair))
    self.population.chromosomes = children
