import importlib.util
import numpy as np

from timeit import default_timer as timer

import simulation.parameters


def load(model):

    # Load a COPY of the model
    spec = importlib.util.find_spec(model)
    model = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(model)

    return model


class Simulation:
    """Simulation manager"""

    def __init__(self, model, **block_parameters):

        # Inherit simulation parameters
        self.solver = simulation.parameters.solver
        self.beg = simulation.parameters.t_beg
        self.end = simulation.parameters.t_end
        self.step = simulation.parameters.sample_time

        # Simulation iterator variables
        self.current_step = 0
        # Estimate total number of simulation steps
        self.last_simulation_step = round((self.end - self.beg) / self.step)

        # Treat total number of simulation steps as an estimate of the
        # logger chunk
        self.chunk = self.last_simulation_step
        self.data = None
        self.offset = 0

        # Assign and parse the model
        self.model = model
        # Find all block definitions
        blockdefs = [att for att in dir(model) if not att.startswith('_')
                     and isinstance(getattr(model, att),
                                    getattr(model, 'BlockDef'))]
        # Create blocks
        for blockdef in blockdefs:
            m, o = getattr(model, blockdef).library.rsplit('.', 1)
            if blockdef in block_parameters:
                p = block_parameters[blockdef]
            else:
                p = getattr(model, blockdef).parameters
            setattr(model,
                    blockdef,
                    getattr(importlib.import_module(m), o)(**p))
        # Remember blocks
        self.blocks = [getattr(model, blockdef) for blockdef in blockdefs]

        # Validate blocks
        for block in self.blocks:
            block.validate(self)

        print("Running '{}' with '{}' solver, ".format(
            model.__name__, self.solver), end='')
        print("for t in [{},{}], with step {}.".format(
            self.beg, self.end, self.step))

    def step(self):
        return self.__call__()

    def run(self, stop_time=None):
        if not stop_time:
            stop_time = self.end
        return self.__call__(stop_time)

    def __call__(self, stop_time=None):

        if not stop_time:
            last_step = self.current_step + 1
        else:
            last_step = round((stop_time - self.beg) / self.step)

        if last_step > self.last_simulation_step:
            last_step = self.last_simulation_step

        # Adopt first and last step to range
        first_step = self.current_step + 1
        last_step = last_step + 1

        start_time = timer()
        try:
            c = 50 / self.last_simulation_step
            for n in range(first_step, last_step):
                self.current_step = n
                self.t = self.beg + n * self.step
                print("\rProgress: [{0:50s}] {1:.1f}%".format(
                    '#' * int(n * c), n*2*c), end="", flush=True)
                self.log(self.model.signal_flow())
            end_time = timer()
            print("\nSimulation completed. "
                  "Total simulation time: {:.2f} s.".format(
                      end_time - start_time))
        except Exception as exception_message:
            print("\x1b[2K\rSimulation aborted: "
                  "'{}'".format(exception_message))
            print("Exception occurrence: t = {} s.".format(self.t))

        return self.data[:self.offset]

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
