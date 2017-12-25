import importlib.util
import numpy as np
import warnings

from pathlib import Path
from timeit import default_timer as timer
from types import ModuleType

from .block import Definition
from .exception_handler import exception_handler


def _formatwarning(message, category, filename, lineno, file=None, line=None):
    print(message)


warnings.showwarning = _formatwarning

# Event messages
finished = "Simulation finished. Use reload()."


def pretty(t):
    """Format duraton time"""

    whole, frac = (x for x in str("{:.6f}".format(t)).rsplit("."))
    if whole != '0':
        whole = float(whole)
        if whole < 999.5:
            return "{:.3g}s".format(t)
        else:
            return "{:.1f}s".format(t)
    else:
        frac = round(float("."+frac)*10**6)
        if frac < 1000:
            return "{:g}us".format(frac)
        elif round(frac/1000) < 100:
            return "{:.2g}ms".format(frac/1000)
        elif round(frac/1000) < 1000:
            return "{:.3g}ms".format(frac/1000)
        else:
            return "{:.4g}ms".format(frac/1000)


class Simulator:
    """Simulator class"""

    @exception_handler
    def __init__(self, model, defaults, **model_blocks_parameters):

        # Status
        self.status = 'init'

        # Report active simulator
        globals()['simulator'] = self

        # Reload arguments
        self._reload_model = model
        self._reload_defaults = defaults
        self._reload_model_block_parameters = model_blocks_parameters

        # Assign or load a COPY of the model
        if isinstance(model, ModuleType):
            self.model = model
        else:
            p = Path(model)
            spec = importlib.util.spec_from_file_location(p.name, p)
            self.model = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(self.model)

        # Parse the model
        # Find all block definitions
        blkdefs = [att for att in dir(self.model) if not att.startswith('_')
                   and isinstance(getattr(self.model, att), Definition)]
        # Create blocks
        for blkdef in blkdefs:
            m, o = getattr(self.model, blkdef).library.rsplit('.', 1)
            m = 'flython.library.' + m
            if blkdef in model_blocks_parameters:
                p = model_blocks_parameters[blkdef]
            else:
                p = getattr(self.model, blkdef).parameters
            setattr(self.model,
                    blkdef,
                    getattr(importlib.import_module(m), o)(blkdef, self, **p))

        # Remember blocks
        self._blocks = [getattr(self.model, blkdef) for blkdef in blkdefs]

        # Inherit simulation parameters
        for att in dir(defaults):
            if att.startswith('_'):
                continue
            if hasattr(self.model, att):
                setattr(self, att, getattr(self.model, att))
            else:
                setattr(self, att, getattr(defaults, att))

        # Simulator variables init
        # Estimate total number of simulation steps
        self.t = self.t_beg
        self.current_step = 0
        self.total_number_of_steps = round(
            (self.t_end - self.t_beg) / self.sample_time)

        # Treat total number of simulation steps
        # as an estimate of the logger chunk
        self._chunk = self.total_number_of_steps
        self.data = None
        self._offset = 0

        # Initialization completed
        self.status = 'ready'

    def __setattr__(self, name, value):
        if name is 'warnings_filter':
            assert value in ("error", "ignore", "always",
                             "default", "module", "once",
                             "optional"), "invalid filter: %r".format(value)
            if value is not "optional":
                warnings.simplefilter(value)

        super().__setattr__(name, value)

    def reload(self):
        self.__init__(self._reload_model,
                      self._reload_defaults,
                      **self._reload_model_block_parameters)

    def run(self, t_stop=None):

        if self.status is 'ready':
            self._start()
        elif self.status is 'finished':
            print(finished)
            return self.data[:self._offset]

        if t_stop:
            return self._run_until(t_stop)
        else:
            return self._run()

    def step(self):

        if self.status is 'ready':
            self._start()
        elif self.status is 'finished':
            print(finished)
            return self.data[:self._offset]

        return self._step()

    def _start(self, *args):

        self.status = 'starting'

        # Perform block validation
        for block in self._blocks:
            block.simulator = self
            block.validate()

        # Generate running message
        print("Running '{}' with '{}' solver, ".format(
            Path(self.model.__file__).name, self.solver), end='')
        print("for t in [{},{}], with step {}.".format(
            self.t_beg, self.t_end, self.sample_time))

    def _run(self):
        self.status = 'running'
        r_ok = "\nSimulation completed. Total simulation time: {}."
        runtime = self._sim(self.total_number_of_steps)
        print(r_ok.format(pretty(runtime)))
        return self.data[:self._offset]

    def _run_until(self, t_stop):
        self.status = 'running_until'
        ru_ok = "\nRun until t={} completed. Partial run time: {}."
        ru_failed = "Run until t={} failed. Simulation already at t={}."
        last_step = round((t_stop - self.t_beg) / self.sample_time)
        if last_step <= self.current_step:
            self.status = 'failed'
            print(ru_failed.format(pretty(t_stop), pretty(self.t)))
            return self.data[:self._offset]
        runtime = self._sim(last_step)
        print(ru_ok.format(self.t, pretty(runtime)))
        return self.data[:self._offset]

    def _step(self):
        self.status = 'step'
        s_ok = "\nStep completed. Total step time: {}."
        runtime = self._sim(self.current_step + 1)
        print(s_ok.format(pretty(runtime)))
        return self.data[:self._offset]

    def _log(self, data):

        # Rearrange data
        array, dtype = None, None
        for el in data:
            # Ensure 2D ndarray
            el[0] = np.array(el[0])
            try:
                if el[0].ndim <= 1:
                    # ZOH interpolation
                    el[0] = el[0]*np.ones((array.shape[0], 1))
                array = np.concatenate((array, el[0]), 1)
                dtype += el[1]

            except ValueError:
                array, dtype = el
        data = np.array(list(zip(*array.T)), dtype)

        # Expand array if necessary
        try:
            if len(self.data) < self._offset + array.shape[0]:
                # Expand data
                self.data = np.append(
                    self.data, np.empty(self._chunk, self.data.dtype))
        except TypeError:
            # Estimate chunk
            self._chunk = max(self._chunk, 100*array.shape[0])
            # Create an empty array given the data dtype
            self.data = np.empty(self._chunk, data.dtype)

        # Store data
        self.data[self._offset:self._offset+array.shape[0]] = data
        self._offset += array.shape[0]

    def _sim(self, last_step):

        c = 50 / self.total_number_of_steps
        start_time = timer()
        # Adopt first and last step to python 'range'
        for n in range(self.current_step + 1, last_step + 1):
            self.current_step = n
            self.t = self.t_beg + n * self.sample_time
            print("\rProgress: [{0:50s}] {1:.1f}%".format(
                '#' * int(n * c), n*2*c), end="", flush=True)
            self._log(self.model.signal_flow())
        end_time = timer()
        # Change status
        if self.current_step >= self.total_number_of_steps:
            self.status = 'finished'
        else:
            self.status = 'active'

        return end_time - start_time

    def warn(self, message):
        end = '\n'
        if self.status in ('running', 'running_until'):
            message = "\x1b[2K\r" + message
        elif self.status is 'step':
            message = "\n" + message
            end = ''
        warnings.warn("Warning: " + message)
