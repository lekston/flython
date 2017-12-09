import numpy as np

from itertools import count

import library.continuous
import library.discrete
import simulation.parameters as parameters


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

        return self.beg + self._n * self.step

    def __iter__(self):
        return self

    def __call__(self, S=None):

        self._S = self._n + 1 if not S else round((S - self.beg) / self.step)

        if self._S > self._N:
            self._S = self._N

        return self


class Simulation:

    def __init__(self, model):

        self.model = model
        self.solver = parameters.solver
        self.t = Time(parameters.t_beg,
                      parameters.t_end,
                      parameters.sample_time)

        # Estimate chunk for logger
        chunk = np.ceil((self.t.end - self.t.beg) / self.t.step)
        self.log = Logger(chunk)

        for element in self.model.contains:

            # Assign simulation
            if isinstance(element, library.continuous.Continuous):
                element._manager = self
                element._solver = None
            # Inherit sample_time
            elif isinstance(element, library.discrete.Discrete):
                if element.sample_time == -1:
                    element.sample_time = self.t.step

    def step(self):
        return self.__call__(self.t())

    def run(self, stop=None):

        if not stop:
            stop = self.t.end

        return self.__call__(self.t(stop))

    def __call__(self, time):

        with Logger() as log:

            for t in time:
                log(self.model.signal_flow(t))

        return [log.data]


class Logger:

    def __init__(self, chunk=200):

        # Initial estimate of chunk
        self.chunk = int(chunk)
        self.data = None
        self.offset = 0

    def __enter__(self):
        return self

    def __call__(self, data):

        array, dtype = None, None

        for el in data:

            # Ensure 2D ndarray
            el[0] = np.array(el[0])
            if el[0].ndim <= 1:
                el[0] = el[0].reshape((-1, 1))

            try:
                if array.shape[0] != el[0].shape:
                    # ZOH interpolation
                    el[0] = el[0]*np.ones((array.shape[0], 1))
                array = np.concatenate((array, el[0]), 1)
                dtype += el[1]

            except AttributeError:
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

    def __exit__(self, exc_type, exc_value, traceback):
        self.data = self.data[:self.offset]
        if not exc_type:
            return True


class SimulationManager:

    def __init__(self, model):

        self.t_beg = parameters.t_beg
        self.t_end = parameters.t_end
        self.sample_time = parameters.sample_time
        self.model = model
        self.log = None

    def __enter__(self):

        for element in self.model.contains:

            # Assign manager
            if isinstance(element, library.continuous.Continuous):
                element._manager = self

            elif isinstance(element, library.discrete.Discrete):
                # Inherit sample_time
                if element.sample_time == -1:
                    element.sample_time = self.sample_time

        return self

    def __iter__(self):

        for n in count(1, 1):
            t = self.t_beg + n * self.sample_time
            if t < self.t_end:
                yield(t)
            else:
                yield(self.t_end)
                break

    def __exit__(self, exc_type, exc_value, tb):

        if not exc_type:
            return True


class LoggerOld:

    def __init__(self, ):

        # Initial estimate of chunk
        self.chunk = np.int(np.ceil(
            (parameters.t_end - parameters.t_beg) / parameters.sample_time))
        self.data = None
        self.offset = 0

    def __enter__(self):
        return self

    def __call__(self, data):

        array, dtype = None, None

        for el in data:

            # Ensure 2D ndarray
            el[0] = np.array(el[0])
            if el[0].ndim <= 1:
                el[0] = el[0].reshape((-1, 1))

            try:
                if array.shape[0] != el[0].shape:
                    # ZOH interpolation
                    el[0] = el[0]*np.ones((array.shape[0], 1))
                array = np.concatenate((array, el[0]), 1)
                dtype += el[1]

            except AttributeError:
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

    def __exit__(self, exc_type, exc_value, traceback):
        self.data = self.data[:self.offset]
        if not exc_type:
            return True
