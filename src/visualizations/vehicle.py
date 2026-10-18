from matplotlib.axes import Axes
from matplotlib.patches import Rectangle

from objects.vehicle import Vehicle


def visualize_vehicle(vehicle: Vehicle, axes: Axes) -> None:
  colors = {
    "truck": "#5eb6a4",
    "car": "#82a9d1",
    "motorcycle": "#edbf75",
    "quadcopter": "#b5a0d0",
  }
  vehicle_type = vehicle.id.split("-")[0]
  color = colors.get(vehicle_type, "lightblue")
  position = (vehicle.rect.x, vehicle.rect.y)
  rectangle = Rectangle(position, vehicle.rect.width, vehicle.rect.height, facecolor=color, edgecolor="black")
  axes.add_patch(rectangle)

  label = vehicle.id.replace("truck-", "T").replace("car-", "C").replace("motorcycle-", "M").replace("quadcopter-", "Q")
  center_x = vehicle.rect.x + vehicle.rect.width / 2
  center_y = vehicle.rect.y + vehicle.rect.height / 2
  axes.text(center_x, center_y, label, fontsize=8, ha="center", va="center")
