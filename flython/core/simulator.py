import importlib.util
import numpy as np
import os

import warnings

from timeit import default_timer as timer
from types import ModuleType

from .block import Definition

# Event messages
start_message = "Running '{}' with '{}' solver, " \
                "for t in [{},{}], with step {}."
failed = "Simulation broken. Try to reload a model."
finished = "Simulation finished. Use reload()."
simulation_completed = "\nSimulation completed. Total simulation time: {}."
run_until_ignored = "Run until t={} ignored. Simulation already at t={}."
run_until_completed = "\nRun until t={} completed. Partial run time: {}."
step_completed = "\nStep completed. Total step time: {}."


def exception_handler(fun):

    def handler(self, *args):
        try:
            fun(self, *args)
        except FileNotFoundError as exc:
            self.status = 'failed'
            print("{}: {}".format(type(exc).__name__, exc))

    return handler


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
        super().__setattr__('status', 'init')

        # Reload arguments
        self._reload_model = model
        self._reload_defaults = defaults
        self._reload_model_block_parameters = model_blocks_parameters

        # Assign or load a COPY of the model
        if isinstance(model, ModuleType):
            self.model = model
        else:
            path = str(model)
            spec = importlib.util.spec_from_file_location( os.path.basename(path),
                                                           os.path.abspath(path) )
            if spec is None:
                Exception("Incorrect spec from {}/{}".format(
                            os.path.parent(path), os.path.basename(path)) )
 
            self.model = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(self.model)

        # Parse the model
        # Find all block definitions
        blkdefs = [attr for attr in dir(self.model)
                            if isinstance(getattr(self.model, attr), Definition)]
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

        # Inherit simulation settings from model or defaults
        for a in defaults._names:
            if hasattr(self.model, a):
                setattr(self, a, getattr(self.model, a))
            else:
                setattr(self, a, getattr(defaults, a))

        # Initialization completed
        self.status = 'ready'

    def __setattr__(self, name, value):
        if self.status is 'active' and name in self._reload_defaults._names:
            self.warn("Simulation is active, '{}' can not be changed.".format(name))
        else:
            super().__setattr__(name, value)

    def _start(self, *args):
        # Set status
        self.status = 'starting'
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
        # Perform block validation
        for block in self._blocks:
            block.simulator = self
            block.validate()
        # Generate start message
        print(start_message.format(
            os.path.basename(self.model.__file__), self.solver,
            self.t_beg, self.t_end, self.sample_time))

    def reload(self):
        self.__init__(self._reload_model,
                      self._reload_defaults,
                      **self._reload_model_block_parameters)

    def run(self, t_stop=None):
        # Chcek current state
        if self.status is 'ready':
            self._start()
        elif self.status is 'failed':
            print(failed)
            return
        elif self.status is 'finished':
            print(finished)
            return self.data[:self._offset]
        # Perform run / run until
        if t_stop:
            self._run_until(t_stop)
        else:
            self._run()
        return self.data[:self._offset]

    def _run(self):
        self.status = 'running'
        print(simulation_completed.format(
            pretty(self._sim(self.total_number_of_steps))))

    def _run_until(self, t_stop):
        self.status = 'running until'
        last_step = round((t_stop - self.t_beg) / self.sample_time)
        if last_step <= self.current_step:
            self.status = 'active'
            print(run_until_ignored.format(pretty(t_stop), pretty(self.t)))
            return
        print(run_until_completed.format(self.t, pretty(self._sim(last_step))))

    def step(self):
        # Chcek current state
        if self.status is 'ready':
            self._start()
        elif self.status is 'failed':
            print(failed)
            return
        elif self.status is 'finished':
            print(finished)
            return self.data[:self._offset]
        # Perform step
        self._step()
        return self.data[:self._offset]

    def _step(self):
        self.status = 'step'
        print(step_completed.format(pretty(self._sim(self.current_step + 1))))

    def _sim(self, last_step):

        c = 50 / self.total_number_of_steps
        start_time = timer()
        # Adopt first and last step to python 'range'
        for n in range(self.current_step + 1, last_step + 1):
            t = self.t_beg + n * self.sample_time
            self.t = t
            self.current_step = n
            print("\rProgress: [{0:50s}] {1:.1f}%".format(
                '#' * int(n * c), n*2*c), end="", flush=True)
            self._log(self.model.signal_flow(t, n))
        end_time = timer()
        # Change status
        if self.current_step >= self.total_number_of_steps:
            self.status = 'finished'
        else:
            self.status = 'active'

        return end_time - start_time

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

    def warn(self, message):
        if self.status in ('running', 'running until'):
            message = "\x1b[2K\rWarning: " + message
        elif self.status is 'step':
            message = "\nWarning: " + message + "\033[F"
        else:
            message = "Warning: " + message
        warnings.warn(message)
