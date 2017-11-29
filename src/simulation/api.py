import simulation.managers as _m

# Import for an interactive session as a shortcut to simulation
# parameters
import simulation.parameters as parameters


def run(*fmodels):
    """Run simulation with given models"""

    # Docelowo tutaj włączony zostanie menadżer logowania
    T = []
    X = []

    for fmodel in fmodels:

        with _m.SimulationManager() as simulation_manager:

            for t in simulation_manager:

                a, b = fmodel(t)

                T.append(a)
                X.append(b)

    return T, X
