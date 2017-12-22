import importlib.util
import numpy as np

from pathlib import Path
from timeit import default_timer as timer
from types import ModuleType

from .block import Definition

step_ok = "\nStep completed. Total step time: {}."
run_ok = "\nSimulation completed. Total simulation time: {0}."
run_until_ok = "\nRun until t={1} completed. Partial run time: {0}."
run_until_failed = "Run until t={} failed. Simulation already at t={}."


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


class Simulation:
    """Simulation manager"""

    def __init__(self, model, defaults, **model_blocks_parameters):

        # Simulator status
        self.status = 'init'

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

    def reload(self):
        self.__init__(self._reload_model,
                      self._reload_defaults,
                      **self._reload_model_block_parameters)

    def run(self,  until=None):

        fromstate = self.status
        self.status = 'run'

        if fromstate is 'ready':
            self._validate()
        else:
            self._run(until)

    def _run(self, until=None):
        if not until:
            self.last_step = self.total_number_of_steps
            msg = run_ok
        else:
            self.last_step = round((until - self.t_beg) / self.sample_time)
            msg = run_until_ok

        if self.last_step <= self.current_step:
            self._run_until_failed(until)
        else:
            runtime = self._sim()
            print(msg.format(pretty(runtime), self.t))

        return self.data[:self._offset]

    def _run_until_failed(self, until):
        self.status = 'run until failed'
        print(run_until_failed.format(pretty(until), pretty(self.t)))

    def step(self):

        fromstate = self.status
        self.status = 'step'

        if fromstate is 'ready':
            self._validate()
        elif fromstate is 'finished':
            self._finished()
        else:
            self._step()

    def _step(self):
        self.status = 'step'
        self.last_step = self.current_step + 1
        runtime = self._sim()
        print(step_ok.format(pretty(runtime)))
        return self.data[:self._offset]

    def _stopped(self):
        self.status = 'stopped'
        if self.current_step >= self.total_number_of_steps:
            self._finished()

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

    def _finished(self, *args):

        fromstate = self.status
        self.status = 'finished'

        if fromstate is 'stopped':
            return None
        else:
            print("Simulation finished. Use reload().")
            return self.data[:self._offset]

    def _sim(self):
        try:
            c = 50 / self.total_number_of_steps
            start_time = timer()
            # Adopt first and last step to python 'range'
            for n in range(self.current_step + 1, self.last_step + 1):
                self.current_step = n
                self.t = self.t_beg + n * self.sample_time
                print("\rProgress: [{0:50s}] {1:.1f}%".format(
                    '#' * int(n * c), n*2*c), end="", flush=True)
                self._log(self.model.signal_flow())
            end_time = timer()
            # Go to stopped
            self._stopped()
        except Exception as exc:
            print("\x1b[2K\rProgress: simulation failed.\n"
                  "{} at t={}s: {}".format(type(exc).__name__, self.t, exc))
            self.status = 'failed'

        return end_time - start_time

    def _validate(self, *args):

        fromstate = self.status
        self.status = 'validating'

        # Perform block validation
        for block in self._blocks:
            block.simulator = self
            block.validate()

        # Generate running message
        print("Running '{}' with '{}' solver, ".format(
            Path(self.model.__file__).name, self.solver), end='')
        print("for t in [{},{}], with step {}.".format(
            self.t_beg, self.t_end, self.sample_time))

        self.run = self._run
        self.step = self._step

        # Change state
        if fromstate is 'run':
            self._run(*args)
        else:
            self._step()

    def _warn(self, message):
        import pdb; pdb.set_trace()

        if self.verbose:
            end = '\n'
            if self.status is 'run':
                message = "\x1b[2K\r" + message
            elif self.status is 'step':
                message = "\n" + message
                end = ''
            print(message, end=end)
