import os
import matplotlib.pyplot as plt
import yaml
from matplotlib.axes import Axes
from matplotlib.patches import Rectangle

from algo.objective import objective
from objects.ship import Ship
from objects.state import State
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


def visualize_ship(ship: Ship, axes: Axes) -> None:
  axes.set_xlim(0, ship.rect.width)
  axes.set_ylim(0, ship.rect.height)
  axes.set_aspect("equal")
  axes.set_xticks(range(ship.rect.width + 1))
  axes.set_yticks(range(ship.rect.height + 1))
  axes.grid()

  for vehicle in ship.vehicles:
    visualize_vehicle(vehicle, axes)


def visualize_state(state: State, save_path: str | None = None) -> plt.Figure:
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

  if save_path:
    figure.savefig(save_path, bbox_inches="tight")

  return figure


def plot_curves(
  history: list[float],
  history_prob: list[float],
  title: str = "Simulated Annealing",
  save_path: str | None = None,
) -> plt.Figure:
  figure, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 7))

  ax1.plot(range(len(history)), history, color="#1f77b4", linewidth=1.5)
  ax1.set_title("Perubahan nilai objective", fontsize=11)
  ax1.set_xlabel("Iterasi", fontsize=9)
  ax1.set_ylabel("Value", fontsize=9)
  ax1.grid(True, linestyle="--", alpha=0.6)

  ax2.plot(range(len(history_prob)), history_prob, color="#1f77b4", linewidth=0.8)
  ax2.set_title("Probabilitas penerimaan neighbor", fontsize=11)
  ax2.set_xlabel("Iterasi", fontsize=9)
  ax2.set_ylabel("Probabilitas", fontsize=9)
  ax2.set_ylim(-0.05, 1.05)
  ax2.grid(True, linestyle="--", alpha=0.6)

  figure.suptitle(title, fontsize=13, fontweight="bold")
  figure.tight_layout()

  if save_path:
    figure.savefig(save_path, bbox_inches="tight")

  return figure


def plot_hc_curve(
  history: list[float] | list[int],
  title: str = "Hill Climbing",
  save_path: str | None = None,
) -> plt.Figure:
  figure, ax = plt.subplots(figsize=(10, 4))
  ax.plot(range(len(history)), history, color="#1f77b4", linewidth=1.5)
  ax.set_title("Perubahan nilai objective", fontsize=11)
  ax.set_xlabel("Iterasi", fontsize=9)
  ax.set_ylabel("Value", fontsize=9)
  ax.grid(True, linestyle="--", alpha=0.6)

  figure.suptitle(title, fontsize=13, fontweight="bold")
  figure.tight_layout()

  if save_path:
    figure.savefig(save_path, bbox_inches="tight")

  return figure


def state_to_dict(state: State) -> dict:
  return {
    "ship": {
      "width": state.ship.rect.width,
      "height": state.ship.rect.height,
      "max_capacity": state.ship.max_capacity,
      "total_weight": sum(v.weight for v in state.ship.vehicles),
      "vehicles": [
        {
          "id": v.id,
          "width": v.rect.width,
          "height": v.rect.height,
          "x": v.rect.x,
          "y": v.rect.y,
          "orientation": v.orientation,
          "weight": v.weight,
          "shipping_fee": v.shipping_fee,
          "eta": v.eta,
        }
        for v in state.ship.vehicles
      ],
    },
    "vehicles_outside": [
      {
        "id": v.id,
        "width": v.rect.width,
        "height": v.rect.height,
        "weight": v.weight,
        "shipping_fee": v.shipping_fee,
        "eta": v.eta,
      }
      for v in state.vehicles_outside
    ],
  }


def save_yaml_report(path: str, report_data: dict) -> None:
  os.makedirs(os.path.dirname(path), exist_ok=True)
  with open(path, "w", encoding="utf-8") as f:
    yaml.safe_dump(report_data, f, sort_keys=False, default_flow_style=False)


def visualize_hc_results(
  initial_state: State | None,
  final_state: State,
  history: list[float] | list[int],
  title: str = "Hill Climbing",
  duration: float | None = None,
  save_dir: str | None = None,
  extra_info: dict | None = None,
) -> None:
  print(f"\n{'='*45}")
  print(f"Hasil Eksperimen: {title}")
  print(f"{'='*45}")
  if initial_state is not None:
    print(f"Objective awal   : {objective(initial_state)}")
  print(f"Objective akhir  : {objective(final_state)}")
  print(f"Banyak iterasi   : {len(history) - 1}")
  if duration is not None:
    print(f"Durasi pencarian : {duration:.4f} detik")
  if extra_info:
    for k, v in extra_info.items():
      print(f"{k:<17}: {v}")
  print(f"{'='*45}")

  init_path = None
  final_path = None
  curve_path = None

  if save_dir:
    os.makedirs(save_dir, exist_ok=True)
    if initial_state is not None:
      init_path = os.path.join(save_dir, "initial_state.png")
      initial_state.save_yaml(os.path.join(save_dir, "initial_state.yaml"))
    final_path = os.path.join(save_dir, "final_state.png")
    final_state.save_yaml(os.path.join(save_dir, "final_state.yaml"))
    curve_path = os.path.join(save_dir, "objective_curve.png")
    yaml_report_path = os.path.join(save_dir, "result.yaml")

    report_data = {
      "algorithm": title,
      "objective_awal": objective(initial_state) if initial_state is not None else None,
      "objective_akhir": objective(final_state),
      "banyak_iterasi": len(history) - 1,
      "durasi_detik": round(duration, 4) if duration is not None else None,
    }
    if extra_info:
      report_data.update(extra_info)
    report_data["final_state"] = state_to_dict(final_state)
    if initial_state is not None:
      report_data["initial_state"] = state_to_dict(initial_state)

    save_yaml_report(yaml_report_path, report_data)
    print(f"Hasil YAML dan grafik disimpan di: {save_dir}\n")

  if initial_state is not None:
    visualize_state(initial_state, save_path=init_path)
  visualize_state(final_state, save_path=final_path)

  plot_title = title
  if duration is not None:
    plot_title += f" (Durasi: {duration:.4f}s, Iterasi: {len(history) - 1})"
  plot_hc_curve(history, title=plot_title, save_path=curve_path)
  plt.show()


def visualize_sa_results(
  initial_state: State | None,
  final_state: State,
  history: list[float],
  history_prob: list[float],
  duration: float | None = None,
  save_dir: str | None = None,
  extra_info: dict | None = None,
) -> None:
  print(f"\n{'='*45}")
  print("Hasil Eksperimen: Simulated Annealing")
  print(f"{'='*45}")
  if initial_state is not None:
    print(f"Objective awal   : {objective(initial_state)}")
  print(f"Objective akhir  : {objective(final_state)}")
  print(f"Banyak iterasi   : {len(history) - 1}")
  if duration is not None:
    print(f"Durasi pencarian : {duration:.4f} detik")
  if extra_info:
    for k, v in extra_info.items():
      print(f"{k:<17}: {v}")
  print(f"{'='*45}")

  init_path = None
  final_path = None
  curve_path = None

  if save_dir:
    os.makedirs(save_dir, exist_ok=True)
    if initial_state is not None:
      init_path = os.path.join(save_dir, "initial_state.png")
      initial_state.save_yaml(os.path.join(save_dir, "initial_state.yaml"))
    final_path = os.path.join(save_dir, "final_state.png")
    final_state.save_yaml(os.path.join(save_dir, "final_state.yaml"))
    curve_path = os.path.join(save_dir, "sa_curves.png")
    yaml_report_path = os.path.join(save_dir, "result.yaml")

    report_data = {
      "algorithm": "Simulated Annealing",
      "objective_awal": objective(initial_state) if initial_state is not None else None,
      "objective_akhir": objective(final_state),
      "banyak_iterasi": len(history) - 1,
      "durasi_detik": round(duration, 4) if duration is not None else None,
    }
    if extra_info:
      report_data.update(extra_info)
    report_data["final_state"] = state_to_dict(final_state)
    if initial_state is not None:
      report_data["initial_state"] = state_to_dict(initial_state)

    save_yaml_report(yaml_report_path, report_data)
    print(f"Hasil YAML dan grafik disimpan di: {save_dir}\n")

  if initial_state is not None:
    visualize_state(initial_state, save_path=init_path)
  visualize_state(final_state, save_path=final_path)

  sa_plot_title = "Simulated Annealing"
  if duration is not None:
    sa_plot_title += f" (Durasi: {duration:.4f}s, Iterasi: {len(history) - 1})"
  plot_curves(history, history_prob, title=sa_plot_title, save_path=curve_path)
  plt.show()


def plot_ga_curves(
  history_max: list[float],
  history_avg: list[float],
  title: str = "Genetic Algorithm",
  save_path: str | None = None,
) -> plt.Figure:
  figure, ax = plt.subplots(figsize=(10, 4))
  iters = range(len(history_max))
  ax.plot(iters, history_max, color="#2c7bb6", linewidth=1.5, label="Maks")
  ax.plot(iters, history_avg, color="#d7191c", linewidth=1.0, linestyle="--", alpha=0.6, label="Rata-rata")
  ax.set_title("Nilai objective populasi per generasi", fontsize=11)
  ax.set_xlabel("Generasi", fontsize=9)
  ax.set_ylabel("Objective", fontsize=9)
  ax.legend(fontsize=9)
  ax.grid(True, linestyle="--", alpha=0.6)

  figure.suptitle(title, fontsize=13, fontweight="bold")
  figure.tight_layout()

  if save_path:
    figure.savefig(save_path, bbox_inches="tight")

  return figure


def visualize_ga_results(
  initial_state: State | None,
  final_state: State,
  history_max: list[float],
  history_avg: list[float],
  population_size: int | None = None,
  generations: int | None = None,
  duration: float | None = None,
  save_dir: str | None = None,
) -> None:
  title = "Genetic Algorithm"

  print(f"\n{'='*45}")
  print(f"Hasil Eksperimen: {title}")
  print(f"{'='*45}")
  if initial_state is not None:
    print(f"Objective awal   : {objective(initial_state)}")
  print(f"Objective akhir  : {objective(final_state)}")
  print(f"Banyak generasi  : {len(history_max) - 1}")
  if population_size is not None:
    print(f"Jumlah populasi  : {population_size}")
  if generations is not None:
    print(f"Maks generasi    : {generations}")
  if duration is not None:
    print(f"Durasi pencarian : {duration:.4f} detik")
  print(f"{'='*45}")

  init_path = None
  final_path = None
  curve_path = None

  if save_dir:
    os.makedirs(save_dir, exist_ok=True)
    if initial_state is not None:
      init_path = os.path.join(save_dir, "initial_state.png")
      initial_state.save_yaml(os.path.join(save_dir, "initial_state.yaml"))
    final_path = os.path.join(save_dir, "final_state.png")
    final_state.save_yaml(os.path.join(save_dir, "final_state.yaml"))
    curve_path = os.path.join(save_dir, "objective_curve.png")
    yaml_report_path = os.path.join(save_dir, os.path.basename(save_dir) + ".yaml")

    report_data: dict = {
      "algorithm": title,
      "objective_awal": objective(initial_state) if initial_state is not None else None,
      "objective_akhir": objective(final_state),
      "banyak_generasi": len(history_max) - 1,
      "durasi_detik": round(duration, 4) if duration is not None else None,
    }
    if population_size is not None:
      report_data["jumlah_populasi"] = population_size
    if generations is not None:
      report_data["maks_generasi"] = generations
    report_data["final_state"] = state_to_dict(final_state)
    if initial_state is not None:
      report_data["initial_state"] = state_to_dict(initial_state)

    save_yaml_report(yaml_report_path, report_data)
    print(f"Hasil YAML dan grafik disimpan di: {save_dir}\n")

  if initial_state is not None:
    visualize_state(initial_state, save_path=init_path)
  visualize_state(final_state, save_path=final_path)

  ga_plot_title = title
  if duration is not None:
    ga_plot_title += f" (Durasi: {duration:.4f}s, Generasi: {len(history_max) - 1})"
  plot_ga_curves(history_max, history_avg, title=ga_plot_title, save_path=curve_path)
  plt.show()
