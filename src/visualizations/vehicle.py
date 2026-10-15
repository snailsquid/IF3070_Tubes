from matplotlib.axes import Axes
from matplotlib.patches import Rectangle

from objects.vehicle import Vehicle

def visualize_vehicle(vehicle: Vehicle, axes: Axes) -> None:
  rectangle = Rectangle(
    (vehicle.rect.x, vehicle.rect.y),
    vehicle.rect.width,
    vehicle.rect.height,
    facecolor="lightblue",
    edgecolor="black",
)
  axes.add_patch(rectangle)
  axes.text(
    vehicle.rect.x + vehicle.rect.width / 2,
    vehicle.rect.y + vehicle.rect.height / 2,
    vehicle.id,
    ha="center",
    va="center",
  )