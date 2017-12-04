import library.discrete


class P(library.discrete.Discrete):

    dtype = [('u', '<f8')]

    def __init__(self, gain, sample_time=-1):

        def f(t, x):
            return x

        def g(x):
            return x * self.u

        self.f = f
        self.g = g

        super().__init__(x=gain, sample_time=sample_time)
