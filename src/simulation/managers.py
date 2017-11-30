import numpy as np
import simulation.parameters as parameters

from itertools import count


class SimulationManager:

    def __init__(self):

        self.t_beg = parameters.t_beg
        self.t_end = parameters.t_end
        self.step_size = parameters.step_size

    def __enter__(self):

        return self

    def __iter__(self):

        for n in count(1, 1):
            t = self.t_beg + n * self.step_size
            if t < self.t_end:
                yield(t)
            else:
                yield(self.t_end)
                break

    def __exit__(self, exc_type, exc_value, tb):

        if not exc_type:
            return True


class Logger:

    def __init__(self, ):

        # Initial estimate of chunk
        self.chunk = np.int(np.ceil(
            (parameters.t_end - parameters.t_beg) / parameters.step_size))
        self.data = None
        self.offset = 0

    def __enter__(self):
        return self

    def __call__(self, data):

        T, *data = data
        # Number of rows
        nrows = T.shape[0]

        # Begin with time array
        array = np.array(T).reshape((-1, 1))
        dtype = [('t', '<f8')]

        for el in data:

            if el[0].shape[0] == nrows:
                if el[0].ndim == 1:
                    array = np.concatenate((array, el[0].reshape((-1, 1))), 1)
                else:
                    array = np.concatenate((array, el[0]), 1)
            elif el[0].shape[0] == 1:
                # ZOH interpolation
                array = np.concatenate((array, el[0]*np.ones((nrows, 1))), 1)

            dtype += el[1]

        data = np.array(list(zip(*array.T)), dtype)

        try:
            if len(self.data) < self.offset + nrows:
                # Expand data
                self.data = np.append(
                    self.data, np.empty(self.chunk, self.data.dtype))
        except TypeError:
            # Estimate chunk
            self.chunk = max(self.chunk, 100*nrows)
            # Create an empty array given the data dtype
            self.data = np.empty(self.chunk, data.dtype)

        # Store data
        self.data[self.offset:self.offset+nrows] = data
        self.offset += nrows

    def __exit__(self, exc_type, exc_value, traceback):
        self.data = self.data[:self.offset]
        if not exc_type:
            return True
