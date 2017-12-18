import importlib.util
import numpy as np

from timeit import default_timer as timer

import simulation.parameters as parameters


def load(model, **parameters):

    # Load a COPY of the model
    spec = importlib.util.find_spec(model)
    model = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(model)

    # Parse COPY of the model
    # Find and instantiate blocks
    blocks = [att for att in dir(model) if not att.startswith('_')
              and isinstance(getattr(model, att), getattr(model, 'Block'))]

    for block in blocks:
        m, o = getattr(model, block).library.rsplit('.', 1)
        if block in parameters:
            p = parameters[block]
        else:
            p = getattr(model, block).parameters
        setattr(model, block, getattr(importlib.import_module(m), o)(**p))

    return model


class Time:

    def __init__(self, t_beg, t_end, step):

        self.beg = t_beg
        self.end = t_end
        self.step = step

        self._N = round((self.end - self.beg) / self.step)
        self._S = self._N
        self._n = 0

    def __next__(self):

        if self._n > self._S - 1:
            raise StopIteration

        self._n += 1

        return (self._n, self.beg + self._n * self.step)

    def __iter__(self):
        return self

    def __call__(self, S=None):

        self._S = self._n + 1 if not S else round((S - self.beg) / self.step)

        if self._S > self._N:
            self._S = self._N

        return self


class Simulation:

    def __init__(self, model, **prameters):

        import pdb; pdb.set_trace()
        print("Running '{}' with '{}' solver, ".format(
            model.__name__, parameters.solver), end='')
        print("for t in [{},{}], with step {}.".format(
            parameters.t_beg, parameters.t_end, parameters.sample_time))

        self.model = model
        self.solver = parameters.solver
        self.t = Time(parameters.t_beg,
                      parameters.t_end,
                      parameters.sample_time)

        # Estimate chunk for the logger
        chunk = np.ceil((self.t.end - self.t.beg) / self.t.step)
        self.log = Logger(chunk)

        for element in self.model.contains:
            element.validate(self)

    def step(self):
        return self.__call__(self.t())

    def run(self, stop=None):

        if not stop:
            stop = self.t.end

        return self.__call__(self.t(stop))

    def __call__(self, time):

        start_time = timer()
        try:
            c = 50 / self.t.end
            for n, t in time:
                print("\rProgress: [{0:50s}] {1:.1f}%".format(
                    '#' * int(t * c), t*2*c), end="", flush=True)
                self.log(self.model(n, t))
            end_time = timer()
            print("\nSimulation completed. "
                  "Total simulation time: {:.2f} s.".format(
                      end_time - start_time))
        except Exception as exception_message:
            print("\x1b[2K\rSimulation aborted: "
                  "'{}'".format(exception_message))
            print("Exception occurrence: t = {} s.".format(t))

        return self.log.data[:self.log.offset]


class Logger:

    def __init__(self, chunk):

        # Initial estimate of chunk
        self.chunk = int(chunk)
        self.data = None
        self.offset = 0

    def __call__(self, data):

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
