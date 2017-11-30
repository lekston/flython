import numpy as np


class P:

    dtype = [('u1', '<f8')]

    def __init__(self, parameters):

        self.parameters = parameters
        self.x = None
        self.y = np.array([0])

    def __call__(self, t, u):

        self.y = self.parameters * u

        return self.y


class Planner:

    dtype = [('r', '<f8')]

    def __init__(self, plan):

        self.plan = plan

    def __call__(self, t, u):

        return self.plan
