import flython.parameters as parameters


def load(model, **model_block_parameters):
    from flython.simulation import Simulation
    return Simulation(model,
                      parameters,
                      **model_block_parameters)
