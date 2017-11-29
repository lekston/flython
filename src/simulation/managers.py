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

    def __call__(self, data):
        step = len(data)
        try:
            if len(self.data) < self.offset + step:
                # Expand data
                self.data = np.append(
                    self.data, np.empty(self.chunk, self.data.dtype))
        except TypeError:
            # Estimate chunk
            self.chunk = max(self.chunk, 100*step)
            # Create an empty array given the data dtype
            self.data = np.empty(self.chunk, data.dtype)

        # Store data
        self.data[self.offset:self.offset+step] = data
        self.offset += step

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.data = self.data[:self.offset]
        if not exc_type:
            return True
