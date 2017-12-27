from .core import parameters


def load(model, **model_block_parameters):
    from .core import Simulator
    return Simulator(model,
                     parameters,
                     **model_block_parameters)
