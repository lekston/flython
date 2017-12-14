#!/opt/local/bin/python
# This is a simple simulation script, tested in Python 3.6.3
import numpy as np
import matplotlib.pyplot as plt

import simulation

from library.continuous.models import SimplifiedLongitudinalMotion
from library.discrete.planners import WaypointXZ, FlightplanXZ
from library.discrete.planners import WindvectorXZ, WindfieldXZ
from library.vehicles import Birde
from library.discrete.controllers import P, PIrD


# Set simulation parameters
simulation.parameters.solver = 'RK45'
simulation.parameters.t_end = 200
simulation.parameters.sample_time = .01

# Flight plan definition
plan = [
    WaypointXZ(0, -300),
    WaypointXZ(2000, -300),
    WaypointXZ(3000, -200),
    WaypointXZ(4000, -200)
]

# Wind field definition
field = [
    WindvectorXZ(0, 0, 0),
    WindvectorXZ(690, 1, 5),
    WindvectorXZ(695, 2, 10),
    WindvectorXZ(700, 3, 15),
    WindvectorXZ(705, 2, 10),
    WindvectorXZ(710, 1, 5),
    WindvectorXZ(715, 0, 0),
]
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
flightplan = FlightplanXZ(plan=plan, sample_time=.1)
windfield = WindfieldXZ(field=field)
tcontroller = PIrD(Kp=.1, Ki=0, Kd=0, sample_time=.1)
tcontroller.dtype = [('tr', '<f8')]
qcontroller = PIrD(Kp=1, Ki=0, Kd=0)
qcontroller.dtype = [('qr', '<f8')]
mcontroller = P(Kp=1)


class Model:

    contains = [vehicle, flightplan, windfield, tcontroller,
                qcontroller, mcontroller]

    @staticmethod
    def signal_flow(t):

        qv, tv, xv, zv = vehicle.x[2:6]
        xr, zr = flightplan(t, xv)

        # Theta controller
        tr = tcontroller(t, zv - zr)
        if np.rad2deg(tr) > 5:
            tr = np.deg2rad(5)
        elif np.rad2deg(tr) < -5:
            tr = np.deg2rad(-5)

        # Pitch controller
        qr = qcontroller(t, tr - tv)

        # Elevator controller
        mr = mcontroller(t, qr - qv)

        # Field of wind
        wind_vel = windfield(t, xv)

        # External inputs for vehicle
        u = [10, mr, *wind_vel]

        # Vehicle
        T, X = vehicle(t, u)

        return ([T, [('t', '<f8')]],
                [X, vehicle.dtype],
                [tr, tcontroller.dtype],
                [qr, qcontroller.dtype],
                [(xr, zr), flightplan.dtype])


simdata = simulation.Simulation(Model).run()

# Render text using TeX interpreter
# plt.rc('text', usetex=True)

# Plot data
f = plt.figure()

# plt.plot(simdata['t'], np.sqrt(u**2 + w**2), marker='o')
plt.plot(simdata['x'], -simdata['z'], marker='o',
         label='Position of a vehicle in vehicle-carried frame')
plt.plot(simdata['xr'], -simdata['zr'],
         label='Reference trajectory')
plt.xlabel('x coordinate')
plt.ylabel('z coordinate')
plt.grid()
f.axes[0].legend(loc='upper center', bbox_to_anchor=(0.5, 1.05),
                 ncol=3, fancybox=True, shadow=True)

f = plt.figure()
# plt.plot(simdata['t'], simdata['z'], marker='o')
u = simdata['u']
w = simdata['w']
plt.plot(simdata['t'], simdata['u'], label='$u(t)$')
plt.plot(simdata['t'], simdata['w'], label='$w(t)$')
plt.plot(simdata['t'], np.sqrt(u**2 + w**2), label=r'$\mathrm{TAS}(t)$')
plt.xlabel('t')
plt.ylabel(r'$u(t), w(t), \mathrm{TAS}(t)$')
f.axes[0].legend()
plt.grid()

f = plt.figure()
plt.plot(simdata['t'], np.rad2deg(np.arctan(w / u)), label=r"$\alpha(t)$")
plt.plot(simdata['t'], np.rad2deg(simdata['theta']),
         label=r"$\Theta(t)$")
plt.step(simdata['t'], np.rad2deg(simdata['tr']), label=r"$\theta_r(t)$")
plt.xlabel('t')
plt.ylabel(r'$\alpha(t), \Theta(t)$')
f.axes[0].legend()
plt.grid()


f = plt.figure()
plt.plot(simdata['t'], np.rad2deg(np.arctan(w / u)), label=r"$\alpha(t)$")
plt.plot(simdata['t'], np.rad2deg(simdata['q']),
         label=r"$q(t)$")
plt.step(simdata['t'], np.rad2deg(simdata['qr']), label=r"$q_r(t)$")
plt.xlabel('t')
plt.ylabel(r'$\alpha(t), q(t)$')
f.axes[0].legend()
plt.grid()
plt.show()
