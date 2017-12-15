import simulation as _simulation

# Import for an interactive session as a shortcut to simulation
# parameters
# import simulation.parameters as parameters


def load(model, **parameters):
    return _simulation.Simulation(model, **parameters)


def run(*models):
    """Run simulation with given models"""

    data = []

    for model in models:

        with _simulation.Logger() as log:

            with _simulation.SimulationManager(model) as simulation_manager:

                for t in simulation_manager:

                    log(model(t))

        data.append(log.data)

    return data
