from objects.ship import Ship
from objects.vehicle import Vehicle, VehicleBuilder
from visualizations.ship import visualize_ship

def init_ship() -> Ship:
  return Ship(5, 10, 999)

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

def main():
  ship: Ship = init_ship()
  vehicles: list[Vehicle] = init_vehicles()
  

if __name__ == "__main__":
  main()
