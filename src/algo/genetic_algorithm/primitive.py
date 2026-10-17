
from abc import ABC, abstractmethod
from mimetypes import init
from typing import Generator

from matplotlib.pylab import Enum
from numpy import cross
import numpy


class Chromosome(ABC):
  def __init__(self) -> None:
    pass
  @abstractmethod
  def fitness(self) -> float:
    pass

class ChromosomeFactoryStrategy(Enum):
  RANDOM = 1

class ChromosomeFactory:
  def __init__(self, strategy: ChromosomeFactoryStrategy = ChromosomeFactoryStrategy.RANDOM) -> None:
    self.strategy = strategy
  def create_chromosome(self) -> Chromosome:
    if self.strategy == ChromosomeFactoryStrategy.RANDOM :
      return self.randomized_chromosome()
    raise RuntimeError("Pick a god damn strategy")

  @abstractmethod
  def randomized_chromosome(self) ->Chromosome:
    pass

class TerminationStrategy(ABC):
  def __init__(self) -> None:
    pass
  @abstractmethod
  def can_terminate(self) -> bool:
    pass

class Population:
  def __init__(self, size: int, ch_factory: ChromosomeFactory) -> None:
    self.size = size
    self.chromosomes = self.__createPopulation()
    self.__factory = ch_factory
  
  def __createPopulation(self) -> list[Chromosome]:
    chromosomes: list[Chromosome]= []
    for i in range(self.size):
      chromosome = self.__factory.create_chromosome()
      chromosomes.append(chromosome)

    return chromosomes

class SelectionStrategy(ABC):
  def __init__(self, probability: float) -> None:
    super().__init__()
  @abstractmethod
  def pick(self, chromosomes: list[Chromosome]) -> Generator:
    pass

class CrossOverStrategy(ABC):
  def __init__(self, probability: float) -> None:
    super().__init__()
    self.probability = probability
  def cross(self, pair: tuple[Chromosome, Chromosome]) -> tuple[Chromosome, Chromosome]:
    if numpy.random.random() < self.probability:
      return self.__cross_algo(pair)
    else: return (pair)
  @abstractmethod
  def __cross_algo(self, pair: tuple[Chromosome, Chromosome]) -> tuple[Chromosome, Chromosome]:
    pass
    
class MutationStrategy(ABC):
  def __init__(self, probability: float) -> None:
    super().__init__()
    self.__probability = probability
  def mutate(self, a: Chromosome) -> None:
    if numpy.random.random() < self.__probability:
      self.__mutate_algo(a)
  @abstractmethod
  def __mutate_algo(self, a: Chromosome) -> None:
    pass

class PairPickingStrategy(ABC):
  def __init__(self) -> None:
    super().__init__()
  def create_pairs(self, chromosomes: list[Chromosome]) -> list[tuple[Chromosome, Chromosome]]:
    initial_count = len(chromosomes)
    pairs = self.__pairs_algo(chromosomes)
    if len(pairs)*2 != initial_count: raise RuntimeError("Either this check harus ganti (probs for ganjil) or bad strat")
    return pairs

  @abstractmethod
  def __pairs_algo(self, chromosomes: list[Chromosome]) -> list[tuple[Chromosome, Chromosome]]:
    pass
    

class GeneticAlgorithm:
  def __init__(self, population: Population, termination_strategy: TerminationStrategy, cross_over_strategy: CrossOverStrategy, selection_strategy: SelectionStrategy, pair_picking_strategy: PairPickingStrategy, mutation_strategy: MutationStrategy) -> None:
    self.population = population
    self.termination_strategy = termination_strategy
    self.cross_over_strategy = cross_over_strategy
    self.selection_strategy = selection_strategy
    self.pair_picking_strategy = pair_picking_strategy
    self.mutation_strategy = mutation_strategy
  def run(self):
    while True:
      self.step()
      if self.termination_strategy.can_terminate(): break

  def termination_check(self):
    return self.termination_strategy.can_terminate()
  def step(self):
    self.select()
    self.cross_over()
    self.mutate()

  def select(self):
    pop = []
    for _ in range(self.population.size):
      pop.append(self.selection_strategy.pick(self.population.chromosomes))
    self.population.chromosomes = pop

  def mutate(self):
    for chromosome in self.population.chromosomes:
      self.mutation_strategy.mutate(chromosome)

  def create_pairs(self):
    return self.pair_picking_strategy.create_pairs(self.population.chromosomes)
  def cross_over(self):
    pairs = self.create_pairs()
    chromosomes: list[Chromosome] = []
    for pair in pairs:
      new = self.cross_over_strategy.cross(pair)
      chromosomes.append(new[0])
      chromosomes.append(new[1])
    self.population.chromosomes = chromosomes
