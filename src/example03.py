#!/opt/local/bin/python
# This is a simple simulation script, tested in Python 3.6.3
import numpy as np
import matplotlib.pyplot as plt

import simulation

from library.continuous.models import SimplifiedLongitudinalMotion
from library.vehicles import Birde

# Set simulation parameters
simulation.parameters.solver = 'RK45'
simulation.parameters.t_end = 100
simulation.parameters.sample_time = .01

# Initial conditions
u0 = 20
w0 = 2
q0 = 0
theta0 = np.deg2rad(1)
x0 = 0
z0 = -300
x = np.array([u0, w0, q0, theta0, x0, z0])

# Define Model
vehicle = SimplifiedLongitudinalMotion(x, vehicle=Birde)


class Model:

    contains = [vehicle]

    @staticmethod
    def signal_flow(t):

        # u = [T, M, wind_vel]
        u = [1.9, 0, 0, 0]

        T, X = vehicle(t, u)

        return ([T, [('t', '<f8')]],
                [X, vehicle.dtype])


simdata = simulation.Simulation(Model).run()

# Render text using TeX interpreter
# plt.rc('text', usetex=True)

# Plot data
f = plt.figure()

# plt.plot(simdata[0]['t'], np.sqrt(u**2 + w**2), marker='o')
plt.plot(simdata[0]['x'], -simdata[0]['z'], marker='o',
         label='Position of a vehicle in vehicle-carried frame')
plt.xlabel('x coordinate')
plt.ylabel('z coordinate')
plt.grid()
f.axes[0].legend(loc='upper center', bbox_to_anchor=(0.5, 1.05),
                 ncol=3, fancybox=True, shadow=True)

f = plt.figure()
# plt.plot(simdata[0]['t'], simdata[0]['z'], marker='o')
u = simdata[0]['u']
w = simdata[0]['w']
plt.plot(simdata[0]['t'], simdata[0]['u'], label='$u(t)$')
plt.plot(simdata[0]['t'], simdata[0]['w'], label='$w(t)$')
plt.plot(simdata[0]['t'], np.sqrt(u**2 + w**2), label=r'$\mathrm{TAS}(t)$')
plt.xlabel('t')
plt.ylabel(r'$u(t), w(t), \mathrm{TAS}(t)$')
f.axes[0].legend()
plt.grid()

f = plt.figure()
plt.plot(simdata[0]['t'], np.rad2deg(np.arctan(w / u)), label=r"$\alpha(t)$")
plt.plot(simdata[0]['t'], np.rad2deg(simdata[0]['theta']),
         label=r"$\Theta(t)$")
plt.xlabel('t')
plt.ylabel(r'$\alpha(t), \Theta(t)$')
f.axes[0].legend()
plt.grid()
plt.show()
