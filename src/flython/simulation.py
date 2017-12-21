import importlib.util
import numpy as np

from pathlib import Path
from timeit import default_timer as timer
from types import ModuleType

from flython.blockset import block


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
        blockdefs = [att for att in dir(self.model) if not att.startswith('_')
                     and isinstance(getattr(self.model, att),
                                    block.Definition)]
        # Create blocks
        for blockdef in blockdefs:
            m, o = getattr(self.model, blockdef).library.rsplit('.', 1)
            m = 'flython.library.' + m
            if blockdef in model_blocks_parameters:
                p = model_blocks_parameters[blockdef]
            else:
                p = getattr(self.model, blockdef).parameters
            setattr(self.model,
                    blockdef,
                    getattr(importlib.import_module(m), o)(**p))
        # Remember blocks
        self.blocks = [getattr(self.model, blockdef) for blockdef in blockdefs]

        # Inherit simulation parameters
        for att in dir(defaults):
            if att.startswith('_'):
                continue
            if hasattr(self.model, att):
                setattr(self, att, getattr(self.model, att))
            else:
                setattr(self, att, getattr(defaults, att))

        # Simulation iter variables
        self.current_step = 0
        # Estimate total number of simulation steps
        self.total_number_of_steps = round(
            (self.t_end - self.t_beg) / self.sample_time)

        # Treat total number of simulation steps may be an estimate of
        # the logger chunk
        self.chunk = self.total_number_of_steps
        self.data = None
        self.offset = 0

    def step(self):
        data, exec_time = self._call()
        print("\nStep completed. Total step time: {}.".format(
            pretty_time(exec_time)))
        return data

    def run(self, stop_time=None):
        if not stop_time:
            stop_time = self.t_end
            msg = ("\nSimulation completed."
                   " Total simulation time: {}.")
        else:
            msg = ("\Run completed."
                   " Total run time: {}.")
        data, exec_time = self._call(stop_time)
        print(msg.format(pretty_time(exec_time)))
        return data

    def _call(self, stop_time=None):

        if self.current_step == 0:
            # Validate blocks
            for block in self.blocks:
                block.validate(self)
            # Generate running message
            print("Running '{}' with '{}' solver, ".format(
                Path(self.model.__file__).name, self.solver), end='')
            print("for t in [{},{}], with step {}.".format(
                self.t_beg, self.t_end, self.sample_time))

        if not stop_time:
            last_step = self.current_step + 1
        else:
            last_step = round((stop_time - self.t_beg) / self.sample_time)

        if last_step > self.total_number_of_steps:
            last_step = self.total_number_of_steps

        # Adopt first and last step to python 'range'
        first_step = self.current_step + 1
        last_step = last_step + 1
        c = 50 / self.total_number_of_steps
        try:
            start_time = timer()
            for n in range(first_step, last_step):
                self.current_step = n
                self.t = self.t_beg + n * self.sample_time
                print("\rProgress: [{0:50s}] {1:.1f}%".format(
                    '#' * int(n * c), n*2*c), end="", flush=True)
                self.log(self.model.signal_flow())
            end_time = timer()
        except Exception as ex:
            print("\x1b[2K\rProgress: simulation aborted!\n"
                  "{} at t={}s: {}".format(type(ex).__name__, self.t, ex))

        return (self.data[:self.offset], end_time - start_time)

    def log(self, data):

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
            if len(self.data) < self.offset + array.shape[0]:
                # Expand data
                self.data = np.append(
                    self.data, np.empty(self.chunk, self.data.dtype))
        except TypeError:
            # Estimate chunk
            self.chunk = max(self.chunk, 100*array.shape[0])
            # Create an empty array given the data dtype
            self.data = np.empty(self.chunk, data.dtype)

        # Store data
        self.data[self.offset:self.offset+array.shape[0]] = data
        self.offset += array.shape[0]
