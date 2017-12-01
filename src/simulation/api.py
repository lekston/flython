import simulation as _simulation

# Import for an interactive session as a shortcut to simulation
# parameters
import simulation.parameters as parameters


def run(*fmodels):
    """Run simulation with given models"""

    data = []

    for fmodel in fmodels:

        with _simulation.Logger() as log:

            with _simulation.SimulationManager() as simulation_manager:

                for t in simulation_manager:

                    log(fmodel(t))

        data.append(log.data)

    return data
