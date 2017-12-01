class Planner:

    dtype = [('r', '<f8')]

    def __init__(self, **parameters):

        self.setpoint = parameters['setpoint']

    def __call__(self, t, u):

        return self.setpoint
