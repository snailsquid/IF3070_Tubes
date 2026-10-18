import matplotlib.pyplot as plt
from matplotlib.axes import Axes

from algo.objective import objective
from objects.ship import Ship
from objects.state import State
from visualizations.vehicle import visualize_vehicle

def visualize_ship(ship: Ship, axes: Axes) -> None:
  axes.set_xlim(0, ship.rect.width)
  axes.set_ylim(0, ship.rect.height)
  axes.set_aspect("equal")
  axes.set_xticks(range(ship.rect.width + 1))
  axes.set_yticks(range(ship.rect.height + 1))
  axes.grid()

  for vehicle in ship.vehicles:
    visualize_vehicle(vehicle, axes)

def visualize_state(state: State) -> None:
  figure = plt.figure(figsize=(10, 6))
  ship_axes = figure.add_subplot(1, 2, 1)
  outside_axes = figure.add_subplot(1, 2, 2)

  visualize_ship(state.ship, ship_axes)

  outside_text = "\n".join(
    f"{vehicle.id} ({vehicle.rect.width}x{vehicle.rect.height}, {vehicle.orientation})"
    for vehicle in state.vehicles_outside
  )

  ship_axes.set_title("Ship")
  outside_axes.set_title("Outside")
  outside_axes.set_axis_off()
  outside_axes.text(0, 1, outside_text if outside_text else "-", va="top", transform=outside_axes.transAxes)

  figure.suptitle(f"Value: {objective(state)}")
  figure.tight_layout(rect=(0, 0, 1, 0.95))
  plt.show()
  plt.close(figure)
