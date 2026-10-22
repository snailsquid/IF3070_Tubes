import os

from algo.simulated_annealing import SimulatedAnnealing
from objects.ship import Ship
from objects.state import StateFactory
from objects.vehicle import Vehicle, VehicleBuilder
from visualizations.ship import visualize_ga_results, visualize_hc_results, visualize_sa_results

OUTPUT_DIR = "../output"


def get_run_dir(algo_name: str) -> str:
  os.makedirs(OUTPUT_DIR, exist_ok=True)
  runs = [0]
  for name in os.listdir(OUTPUT_DIR):
    full = os.path.join(OUTPUT_DIR, name)
    if os.path.isdir(full) and name.startswith(f"{algo_name}_run"):
      try:
        num = int(name.split("_run")[1])
        runs.append(num)
      except Exception:
        pass
  next_run = max(runs) + 1
  run_dir = os.path.join(OUTPUT_DIR, f"{algo_name}_run{next_run}")
  os.makedirs(run_dir, exist_ok=True)
  return run_dir


def init_ship() -> Ship:
  return Ship(5, 6, 4500)


def init_vehicles() -> list[Vehicle]:
  builder = VehicleBuilder()
  return [
    builder.car(),
    builder.car(),
    builder.car(),
    builder.truck(),
    builder.truck(),
    builder.truck(),
    builder.truck(),
    builder.motorcycle(),
    builder.motorcycle(),
    builder.motorcycle(),
    builder.quadcopter(),
    builder.quadcopter(),
    builder.quadcopter(),
  ]


def main() -> None:
  ship = init_ship()
  vehicles = init_vehicles()
  state_factory = StateFactory(ship, vehicles)

  while True:
    print("\n" + "=" * 45)
    print("         PILIH ALGORITMA PENCARIAN           ")
    print("=" * 45)
    print("1. Steepest Ascent Hill Climbing")
    print("2. Hill Climbing with Sideways Move")
    print("3. Stochastic Hill Climbing")
    print("4. Random Restart Hill Climbing")
    print("5. Simulated Annealing")
    print("6. Genetic Algorithm")
    print("0. Keluar")
    print("=" * 45)

    choice = input("Pilih algoritma (0-6): ").strip()

    if choice == "0":
      break

    elif choice == "5":
      print("\nMenjalankan Simulated Annealing...")
      algorithm = SimulatedAnnealing(state_factory)
      state = algorithm.run()
      run_dir = get_run_dir("Simulated_Annealing")
      visualize_sa_results(
        initial_state=algorithm.initial_state,
        final_state=state,
        history=algorithm.history,
        history_prob=algorithm.history_probability,
        duration=algorithm.duration,
        save_dir=run_dir,
      )

    else:
      print("Pilihan tidak valid, silakan coba lagi.")

if __name__ == "__main__":
  main()