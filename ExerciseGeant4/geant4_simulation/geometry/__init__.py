"""Construct the detector geometries.

This subpackage provides a set of geometries that can be used during
simulations. Each geometry is defined in its own module. The
definition of the geometries is done by defining a class inherited
from the ``G4VUserDetectorConstruction`` class.

Classes
=======

The available geometry classes are:
"""

__author__ = 'Maximilian Burkart'

import glob
import os


def trim_path(path):
    return os.path.basename(path).split(".")[0]

# Get a list of all python files without underscores in the geometry
# directory.
directory = "."
file_list = glob.glob(directory + '/geant4_simulation/geometry/[!_]*.py')

# Separate the paths from the file names and cut off the file specifier.
det_list = list(map(trim_path, file_list))

__all__ = det_list
