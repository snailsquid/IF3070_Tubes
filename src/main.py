import os

from algo.genetic_algorithm.implementation import GARunner
from algo.Random_Restart_HC import RandomRestartHillClimb
from algo.Sideways_Move_HC import SidewaysMoveHillClimb
from algo.Steepest_Ascend_HC import SteepestAscentHillClimb
from algo.Stochastic_HC import StochasticHillClimb
from objects.ship import Ship
from objects.state import StateFactory
from objects.vehicle import Vehicle, VehicleBuilder
from visualizations.ship import visualize_ga_results, visualize_hc_results

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
    print("5. Genetic Algorithm")
    print("0. Keluar")
    print("=" * 45)

    choice = input("Pilih algoritma (0-5): ").strip()

    if choice == "0":
      break

    if choice == "1":
      print("\nMenjalankan Steepest Ascent Hill Climbing...")
      algo = SteepestAscentHillClimb(state_factory)
      algo.run()
      run_dir = get_run_dir("Steepest_Ascent_HC")
      algo.visualize(save_dir=run_dir)

    elif choice == "2":
      raw_sm = input("Masukkan batas sideways moves [default: 100]: ").strip()
      max_sm = int(raw_sm) if raw_sm.isdigit() else 100
      print(f"\nMenjalankan Hill Climbing with Sideways Move (max_sideways={max_sm})...")
      algo = SidewaysMoveHillClimb(state_factory, max_sideways=max_sm)
      algo.run()
      run_dir = get_run_dir("Sideways_Move_HC")
      algo.visualize(save_dir=run_dir)

    elif choice == "3":
      print("\nMenjalankan Stochastic Hill Climbing...")
      algo = StochasticHillClimb(state_factory)
      algo.run()
      run_dir = get_run_dir("Stochastic_HC")
      algo.visualize(save_dir=run_dir)

    elif choice == "4":
      raw_rr = input("Masukkan batas restart [default: 10]: ").strip()
      max_rr = int(raw_rr) if raw_rr.isdigit() else 10
      print(f"\nMenjalankan Random Restart Hill Climbing (max_restarts={max_rr})...")
      algo = RandomRestartHillClimb(state_factory, max_restarts=max_rr)
      algo.run()
      run_dir = get_run_dir("Random_Restart_HC")
      algo.visualize(save_dir=run_dir)

    elif choice == "5":
      raw_pop = input("Jumlah populasi [default: 16]: ").strip()
      raw_gen = input("Banyak generasi [default: 100]: ").strip()
      pop_size = int(raw_pop) if raw_pop.isdigit() else 16
      gen_count = int(raw_gen) if raw_gen.isdigit() else 100
      print(f"\nMenjalankan Genetic Algorithm (populasi={pop_size}, generasi={gen_count})...")
      algo_ga = GARunner(state_factory, population_size=pop_size, generations=gen_count)
      final_state = algo_ga.run()
      run_dir = get_run_dir("Genetic_Algorithm")
      visualize_ga_results(
        initial_state=algo_ga.initial_state,
        final_state=final_state,
        history_max=algo_ga.history,
        history_avg=algo_ga.history_avg,
        population_size=algo_ga.population_size,
        generations=algo_ga.generations,
        duration=algo_ga.duration,
        save_dir=run_dir,
      )

    else:
      print("Pilihan tidak valid, silakan coba lagi.")


if __name__ == "__main__":
  main()
