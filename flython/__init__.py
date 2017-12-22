import flython.core.parameters as parameters


def load(model, **model_block_parameters):
    from flython.core import Simulation
    return Simulation(model,
                      parameters,
                      **model_block_parameters)
