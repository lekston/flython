import numpy as np
import simulation.parameters as parameters

from itertools import count

import library.discrete


class SimulationManager:

    def __init__(self, model):

        self.t_beg = parameters.t_beg
        self.t_end = parameters.t_end
        self.sample_time = parameters.sample_time

        import pdb; pdb.set_trace()
        
        for obj in model.contains:

            if isinstance(obj, library.discrete.Discrete):
                print('Jest')

    def __enter__(self):

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


class Logger:

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
