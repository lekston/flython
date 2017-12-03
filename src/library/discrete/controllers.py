import library.discrete


class P(library.discrete.Discrete):

    dtype = [('u', '<f8')]

    def __init__(self, gain, sample_time):

        def f(t, x):
            pass

        def g(x):
            return self.gain * self.u

        self.f = f
        self.g = g

        self.gain = gain
        self.sample_time = sample_time

        super().__init__()
