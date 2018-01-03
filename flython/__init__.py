import warnings

from . import defaults
from .core import block
from .core import discrete
from .core.continuous import Continuous
from .core.logger import logger
from .core import settings as settings_module
from .core.simulator import Simulator


def _formatwarning(message, category, filename, lineno, file=None, line=None):
    print(message)


warnings.showwarning = _formatwarning

settings = settings_module.FlythonSettings(defaults)


def load(model, **model_block_parameters):
    return Simulator(model,
                     settings_module.SimulationSettings(defaults),
                     **model_block_parameters)


logger.info('***** NEW FLYTHON SESSION *****')
