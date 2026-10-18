from objects.state import State

def objective(state: State) -> int:
  return state.get_objective()
