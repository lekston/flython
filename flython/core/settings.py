import warnings

from . import logger as logger_module

logger = logger_module.logger


def exception_handler(fun):

    def handler(self, *args):
        try:
            fun(self, *args)
        except Exception as exc:
            print("{}: {}".format(type(exc).__name__, exc))

    return handler


indent = 0


class Settings:

    def __init__(self, defaults):
        for name in self._names:
            setattr(self, name, getattr(defaults, name))

    def __repr__(self):
        global indent
        line = ''
        for name in dir(self):
            if name.startswith('_'):
                continue
            elif isinstance(getattr(self, name), Settings):
                line += (indent*'   ' + f'{name}:\n')
                indent += 1
                for s in str(getattr(self, name)).split('\n'):
                    line += (f'{s}\n')
                indent -= 1
            else:
                line += indent*'   '
                line += '{} := {}\n'.format(
                    name, getattr(self, name).__repr__())
        line = line[:-1]
        return line


class SimulationSettings(Settings):

    _names = ('solver', 't_beg', 't_end', 'sample_time')


class FlythonSettings(Settings):

    _names = ('warnings_filter', 'file_logger', 'console_logger')

    @exception_handler
    def __setattr__(self, name, value):
        if name is 'warnings_filter':
            assert value in (
                "error", "ignore", "always", "default",
                "module", "once", "interpreter"), \
                f"Invalid value of {name}: '{value}'"
            if value is not "interpreter":
                logger.debug(f'parameters.{name}={value}')
                warnings.resetwarnings()
                warnings.simplefilter(value, UserWarning)
        elif name in ('file_logger', 'console_logger'):
            assert value in (
                "debug", "info", "warning", "error", "critical"), \
                f"Invalid value of {name}: '{value}'"
            getattr(logger_module, name)(value)
            logger.debug(f'parameters.{name}={value}')

        super().__setattr__(name, value)
