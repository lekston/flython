# This is a simple simulation script, tested in Python 3.6.3
import numpy as np

from objects import Aircraft
from models import SimpleTestModel

# Advanced configuration can be done through the simanager module. Look
# inside the module file to see what sort of setup is possible.
import simanager

# Set verbose to True to see the simulation output
simanager.verbose = True

# Set step_size
simanager.step_size = 0.01

# Create Aircraft instance
vehicle = Aircraft(SimpleTestModel, np.array([0.0]))

# Aircraft instance is callable! To run simulation simply
# call the instance.
vehicle()
