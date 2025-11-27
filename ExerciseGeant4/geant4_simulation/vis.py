"""Visualize the detector and the trajectories generated in one event.

This module creates a window with the OpenGLImmediateX visualisation driver
and defines a model for the colors of the trajectories. This model is based
on the ID of the particles used during the simulation. A function to draw
the detector geometry in the window is provided.
"""

__author__ = 'Maximilian Burkart'

import os
import subprocess
from IPython.display import Image, display

from Geant4 import *


def initialize():
    gUImanager.ExecuteMacroFile("geant4_simulation/vis_dawn.mac")
    return


def draw_run():
    # Get last written .prim file to convert it with dawn
    f_to_conv = max(filter(lambda x: x.endswith(".prim"), os.listdir()),
                    key=os.path.getctime)
    # Convert the .prim file to an eps graphic.
    subprocess.run(["dawn",
                    "-d",
                    f_to_conv],
                   stderr=subprocess.DEVNULL)
    # Convert the eps graphic to png graphic.
    subprocess.run(["gs",
                    "-DEPSCrop", "-dSAFER", "-sDEVICE=png256",
                    "-r600",
                    "-o",
                    "event_raw.png",
                    f_to_conv.replace(".prim", ".eps")],
                   stdout=subprocess.DEVNULL)
    subprocess.run(["convert",
                    "event_raw.png",
                    "-trim",
                    "event.png"
                   ])
    display(Image("event.png", width=500))
    return




def setup_raytrace():
    gApplyUICommand("/vis/open RayTracer")
    gApplyUICommand("/vis/rayTracer/headAngle 340.")
    gApplyUICommand("/vis/rayTracer/trace test.jpg")
    return

def draw_volume():
    """Add the detector geometry to the scene.

    This function is called after the initialisation of the Geant4 kernel to
    visualize the detector before starting a run.
    """
    gApplyUICommand("/vis/scene/add/volume")
    gApplyUICommand("/vis/sceneHandler/attach")
    gApplyUICommand("/vis/viewer/flush")
