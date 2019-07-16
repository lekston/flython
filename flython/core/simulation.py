import importlib.util
import numpy as np
import os

from timeit import default_timer as timer
from types import ModuleType

from .block import Definition


def pretty_time(t):
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
            print(spec)
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
                    getattr(importlib.import_module(m), o)(**p))
        # Remember blocks
        self._blocks = [getattr(self.model, blkdef) for blkdef in blkdefs]

        # Inherit simulation parameters
        for att in dir(defaults):
            if hasattr(self.model, att):
                setattr(self, att, getattr(self.model, att))
            else:
                setattr(self, att, getattr(defaults, att))

        # Simulation iter variables
        self.current_step = 0
        self.t = self.t_beg
        # Estimate total number of simulation steps
        self.total_number_of_steps = round(
            (self.t_end - self.t_beg) / self.sample_time)

        # Treat total number of simulation steps may be an estimate of
        # the logger chunk
        self._chunk = self.total_number_of_steps
        self.data = None
        self._offset = 0

    def step(self):
        return self._call('step')

    def run(self, stop_time=None):
        if not stop_time:
            return self._call('run')
        else:
            return self._call('run until', stop_time)

    def reload(self):
        self.__init__(self._reload_model,
                      self._reload_defaults,
                      **self._reload_model_block_parameters)

    def _call(self, mode, stop_time=None):

        if self.current_step == 0:
            # Validate blocks
            for block in self._blocks:
                block.validate(self)
            # Generate running message
            print("Running '{}' with '{}' solver, ".format(
                os.path.basename(self.model.__file__), self.solver), end='')
            print("for t in [{},{}], with step {}.".format(
                self.t_beg, self.t_end, self.sample_time))
        elif self.current_step >= self.total_number_of_steps:
            print("Simulation is completed and exhausted. "
                  "Use reload().")
            return self.data[:self._offset]

        if mode == 'step':
            last_step = self.current_step + 1
        elif mode == 'run':
            last_step = self.total_number_of_steps
        else:
            # Assume run until
            last_step = round((stop_time - self.t_beg) / self.sample_time)
            if last_step > self.total_number_of_steps:
                last_step = self.total_number_of_steps
            if last_step <= self.current_step:
                print("Run until t={} ignored. "
                      "Simulation already at t={}.".format(
                          pretty_time(stop_time), pretty_time(self.t)))
                return self.data[:self._offset]

        # Adopt first and last step to python 'range'
        first_step = self.current_step + 1
        last_step = last_step + 1
        c = 50 / self.total_number_of_steps
        try:
            start_time = timer()
            for n in range(first_step, last_step):
                t = self.t_beg + n * self.sample_time
                self.current_step = n
                self.t = t
                print("\rProgress: [{0:50s}] {1:.1f}%".format(
                    '#' * int(n * c), n*2*c), end="", flush=True)
                self._log(self.model.signal_flow(t, n))
            end_time = timer()
        except Exception as ex:
            print("\x1b[2K\rProgress: simulation aborted!\n"
                  "{} at t={}s: {}".format(type(ex).__name__, self.t, ex))

        if mode == 'step':
            print("\nStep completed. Total step time: {}.".format(
                pretty_time(end_time - start_time)))
        elif mode == 'run':
            print("\nSimulation completed."
                  " Total simulation time: {}.".format(
                      pretty_time(end_time - start_time)))
        else:
            print("\nRun until t={} completed."
                  " Partial run time: {}.".format(
                      pretty_time(self.t), pretty_time(end_time - start_time)))

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
