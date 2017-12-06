import library.discrete


class P(library.discrete.Discrete):

    dtype = [('u', '<f8')]

    def __init__(self, gain, sample_time=-1):

        def g(x):
            return x * self.u

        super().__init__(x=gain, g=g, sample_time=sample_time)
