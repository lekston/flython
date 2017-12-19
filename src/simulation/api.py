import simulation as _simulation

# Import for an interactive session as a shortcut to simulation
# parameters
# import simulation.parameters as parameters


def load(model, **parameters):
    model = _simulation.load(model)
    return _simulation.Simulation(model, **parameters)
