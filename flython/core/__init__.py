import warnings

from .continuous import Continuous
from . import defaults
from . import discrete
from .logger import logger
from .simulator import Simulator


def _formatwarning(message, category, filename, lineno, file=None, line=None):
    print(message)


warnings.showwarning = _formatwarning


def exception_handler(fun):

    def handler(self, *args):
        try:
            fun(self, *args)
        except Exception as exc:
            print("{}: {}".format(type(exc).__name__, exc))

    return handler


class Defaults:

    _locals = ['solver', 't_beg', 't_end', 'sample_time']
    _globals = ['warnings_filter']

    def __init__(self, defaults):
        for name in self._locals + self._globals:
            setattr(self, name, getattr(defaults, name))

    @exception_handler
    def __setattr__(self, name, value):
        if name is 'warnings_filter':
            assert value in ("error", "ignore", "always", "default",
                             "module", "once", "interpreter"), \
                             "Invalid warnings_filter: '{}'".format(value)
            if value is not "interpreter":
                logger.debug(f'warnings_filter={value}')
                warnings.resetwarnings()
                warnings.simplefilter(value, UserWarning)
        # recalculate certian variables when changing sample time
        super().__setattr__(name, value)


parameters = Defaults(defaults)
