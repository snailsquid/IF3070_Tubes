
from abc import ABC, abstractmethod
from typing import Generator

from matplotlib.pylab import Enum


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
  def setPopulation(self, population):
    self.population = population

class Population:
  def __init__(self, size: int, ch_factory: ChromosomeFactory) -> None:
    self.size = size
    self.__createPopulation()
    self.__factory = ch_factory
    self.generation_count = 0
  
  def __createPopulation(self) -> list[Chromosome]:
    chromosomes: list[Chromosome]= []
    for i in range(self.size):
      chromosome = self.__factory.create_chromosome()
      chromosomes.append(chromosome)

    return chromosomes

class SelectionStrategy(ABC):
  def __init__(self, chromosomes: list[Chromosome]) -> None:
    super().__init__()
    self.chromosomes: list[Chromosome] = chromosomes
  @abstractmethod
  def pick(self) -> Generator:
    pass

class CrossOverStrategy(ABC):
  def __init__(self) -> None:
    super().__init__()
  @abstractmethod
  def cross(self, a: Chromosome, b: Chromosome) -> Chromosome:
    pass
    
class MutationStrategy(ABC):
  def __init__(self) -> None:
    super().__init__()
  @abstractmethod
  def mutate(self, a):
    pass

class GeneticAlgorithm:
  def __init__(self, population: Population, termination_strategy: TerminationStrategy, cross_over_strategy: CrossOverStrategy, selection_strategy: SelectionStrategy, mutation_strategy: MutationStrategy) -> None:
    self.population = population
    self.termination = termination_strategy
    self.termination.setPopulation(population)
    self.cross_over_strategy = cross_over_strategy
    self.selection_strategy = selection_strategy
    self.mutation_strategy = mutation_strategy
  def run(self):
    self.population