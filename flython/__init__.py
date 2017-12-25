import flython.parameters as parameters


def load(model, **model_block_parameters):
    from flython.core import Simulator
    return Simulator(model,
                     parameters,
                     **model_block_parameters)
