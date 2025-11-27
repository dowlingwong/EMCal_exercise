"""Control Geant4.

This package provides the functionalities needed to control the Geant4
kernel. In order to do so the ``ApplicationManager`` class is defined.
Auto-completion is also activated for use in interactive mode.

Subpackages
-----------
geometry : Define detector geometries.

Modules
-------
actions : Define action classes and readout functions.

libphyslist : Define additional physics lists.

materials : Define detector materials.

vis : Visualize the detector and events.

Classes
-------
ApplicationManager : Control the Geant4 application.

Compatibility
-------------
The current version of the package is compatible with Geant4.10.6.
"""

__author__ = 'Maximilian Burkart'

import glob

import numpy as np

from Geant4 import *

import geant4_simulation.materials
import geant4_simulation.vis
from geant4_simulation.geometry import *
import geant4_simulation.actions
import geant4_simulation.libphyslist


class ApplicationManager():
    """Control a Geant4 application.

    This class provides an easy way to control the
    workflow of a Geant4 application and to change parameters of
    the simulation. It allows the analysis of simulated events.
    """

    def __init__(self):
        """Set default values.

        The default values for the *geom* and *physicsList* instance
        variables are set and the *is_initialized* flag is set to ``False``.
        """
        self.geom = 'default'
        self.physicsList = 'QGSP_BERT'
        self.is_initialized = False
        self.is_vis_init = False

    def set_geometry(self, geometryName):
        """Set the geometry.

        Specify the ``G4VUserDetectorConstruction`` class used to describe
        the detector geometry during the simulation. This method has to be
        invoked before calling the *initialize()* method. The method is also
        used to change the geometry between two runs. Additional arguments may
        be passed to this method like one would call the object itself, e.g.::

            set_geometry('pbbox(length=40)')

        :param str geometryName: Name of the
           ``G4VUserDetectorConstruction`` class that
           should be used during the simulation.
        """
        if not (hasattr(geant4_simulation.geometry, geometryName.split("(")[0])):
            raise ValueError('Provided geometry does not exist! '
                             'Please choose a different geometry.')
        self.geom = geometryName

    def set_physics_list(self, physList):
        """Set the physics list.

        Specify the physics list used during the simulation.

        :param str physList:
            Name of the physics list. Possible physics lists include the
            lists defined in the :mod:`libphyslist` submodule and the lists
            provided by the Geant4Py module.
        """
        if physList in dir(libphyslist):
            self.physicsList = 'libphyslist.' + physList
        elif physList in dir(G4physicslists):
            self.physicsList = physList
        else:
            available_lists = list(set(filter(lambda x: not x.startswith('_'),
                                           dir(libphyslist)))
                                   | set(filter(lambda x: not x.startswith('_'),
                                           dir(G4physicslists))))
            raise ValueError('No valid physics list provided.'
                             'Available physics lists are {}!'.format(available_lists))

    def initialize(self):
        """Initialize the Geant4 kernel.

        This method creates and passes the three mandatory and the additional
        user action classes to the ``RunManager``. The ``Initialize()``
        method of the ``RunManager`` is then invoked to initialize the
        detector. This method must be called before starting the first run.
        Depending on the state the ``is_initialized`` flag is in, all action
        classes are either assigned to the ``RunManager`` instance or only
        the new geometry is initialized. The re-initialization of the geometry
        takes place if the flag holds true.
        """
        global primaryInit, posX, detector, trackAction, stepAction, physList
        global runAction
        # Seperate the name of the detector and the arguments. If no argument
        # is provided, to braces are added to insure the correct calling of
        # the object.
        for index, char in enumerate(self.geom):
            if char == '(':
                argument = self.geom[index:]
                self.geom = self.geom[:index]
                break
            else:
                argument = '()'
        # Use the seperated detector and parameters to create an instance of
        # DetectorConstruction class. If a wrong name is given, the lead box
        # is built.
        try:
            detector = eval(self.geom + '.' + self.geom + argument)
        except (AttributeError, NameError):
            print('This is no valid geometry! \n Choosing a lead box instead...')
            detector = pbbox.pbbox()

        if self.is_initialized:
            # Create the new world volume.
            gRunManager.SetUserInitialization(detector)
            gRunManager.DefineWorldVolume(detector.Construct())
            # Adjust the origin of the primary particle to the new geometry.
            primaryInit.particleGun.SetParticlePosition(
                G4ThreeVector(-detector.worldX,0,0))
            geant4_simulation.vis.initialize()
        else:
            gRunManager.SetUserInitialization(detector)
            # Initialize the physics list.
            physList = eval(self.physicsList + '()')
            gRunManager.SetUserInitialization(physList)
            # Initialize the primary generator.
            posX = -detector.worldX
            primaryInit = actions.PrimaryGenerator(
                position=G4ThreeVector(posX,0,0),
                numberOfParticles=1)
            gRunManager.SetUserAction(primaryInit)
            # Create and pass the additional action classes to the RunManager
            # instance.
            trackAction = actions.TrackingAction()
            gRunManager.SetUserAction(trackAction)
            stepAction = actions.SteppingAction()
            gRunManager.SetUserAction(stepAction)
            runAction = actions.RunAction(stepAction, trackAction)
            gRunManager.SetUserAction(runAction)
            # Call the Initialize method of the RunManager and change the
            # value of the flag.
            gRunManager.Initialize()
            self.is_initialized = True

        # vis.draw_volume()

    #-------------------------------------------------------------------------
    #define functions used to change the properties of the primary particle
    #-------------------------------------------------------------------------

    def set_particle(self, particle):
        """Set the primary particle.

        Specify the primary particle the ParticleGun is going to use in the
        following events. If the particle is referenced to by an integer, this
        integer is the representation of the particle in terms of the Monte
        Carlo particle numbering scheme.

        .. tabularcolumns: |l|r|
        :param particle:
            Identifier of the particle. If the particle is referenced to by
            an integer, this integer is the representation of the Monte Carlo
            particle numbering scheme. Some string and integer representations
            of common particles are given in the table below.

            ========================= ============
            string representation     PDG code
            ========================= ============
                       e-                 11
                       e+                -11
                      mu-                 13
                      mu+                -13
                      pi+                211
                     gamma                22
            ========================= ============
        :type particle: str or int
        """
        primaryInit.particleGun.SetParticleDefinition(
            gParticleTable.FindParticle(particle))
    #-------------------------------------------------------------------------

    def set_energy(self, energy):
        """Set the energy of the primary particle.

        :param float energy:
            Kinetic energy of the primary particle in GeV.
        """
        energy *= 1.*GeV
        primaryInit.particleGun.SetParticleEnergy(energy)
    #-------------------------------------------------------------------------

    def set_numberOfParticles(self, nOfParticles):
        """Set the number of particles.

        :param int nOfParticles:
            Number of primary particles simultanously generated in one event.
        """
        primaryInit.particleGun.SetNumberOfParticles(nOfParticles)
    #-------------------------------------------------------------------------

    def start_run(self, numberOfEvents=1, visualize=False):
        """Start a run.

        :param int numberOfEvents:
            Number of events simulated in the started run.

            Default is 1.

        :param int vis:
            Draw option. If the value is ``0``, visualization is
            disabled.

            Default is ``1``.
        """
        if visualize and not self.is_vis_init:
            vis.initialize()
            self.is_vis_init = True
        if visualize:
            gApplyUICommand("/vis/enable")
        else:
            gApplyUICommand("/vis/disable")
        gRunManager.BeamOn(numberOfEvents)
        if visualize:
            vis.draw_run()
    #-------------------------------------------------------------------------

    def change_material(self, material="Iron"):
        """Change the material of the :class:`~pbbox` geometry.

        This method enables switching between lead and iron as the material
        the :class:`~pbbox`'s Target volume is built of.
        """
        if not "pbbox" in self.geom:
            raise NotImplementedError('The change of materials is only supported '
                                      'for the pbbox geometry.')
        gGeometryManager.OpenGeometry(detector.physicalTarget)
        logVol = detector.physicalTarget.GetLogicalVolume()
        boxMat = logVol.GetMaterial()
        if material.lower() == "iron" or material.lower() == "fe":
            logVol.SetMaterial(materials.Fe)
            print('Target material has been set to iron...')
        elif material.lower() == "lead" or material.lower() == "pb":
            logVol.SetMaterial(materials.Pb)
            print('Target material has been set to lead...')
        else:
            raise ValueError('Currently only lead and iron are '
                             'supported as materials.')
        gGeometryManager.CloseGeometry()
        gRunManager.GeometryHasBeenModified()
    #-------------------------------------------------------------------------

    def get_x_of_first_vertex(self):
        """Calculate the x coordinate of the first vertex.

        Loop over all secondary particles and find the vertex where the first
        secondary particle is created.

        :return:
           The x coordinate of the creation vertex of the first secondary
           particle.
        :rtype: float
        """
        # Get the x coordinates of all vertices and the track ID of the mother
        # tracks.
        parentIDs = gRunManager.GetUserTrackingAction().preTrackIDList
        vertices = gRunManager.GetUserTrackingAction().vertexList
        # Get the instance of the G4VUserDetectorConstruction class.
        readoutGeometry = gRunManager.GetUserDetectorConstruction()
        primaryID = 1
        # Set the starting value of the minimum to the end of the detector.
        minimumX = 2*readoutGeometry.worldX
        # Loop over all secondary particles.
        for i,ID in enumerate(parentIDs):
            # Find the particles created by the primary particle.
            if ID == primaryID:
                # Update the minimal value of the vertices x coordinate.
                if vertices[i] + readoutGeometry.worldX < minimumX:
                    minimumX = vertices[i] + readoutGeometry.worldX

        return minimumX/cm
    #--------------------------------------------------------------------------

    def get_edep_in_volume(self, volumeName):
        """Calculate the energy deposited in a volume.

        :param str volumeName:
           Name of the volume.

        :return:
           The energy deposited in the volume in GeV.
        :rtype: float
        """
        # Get the name of the volume the energy is deposited in and the
        # deposited energy.
        nameList = gRunManager.GetUserSteppingAction().geomNameList
        edep = gRunManager.GetUserSteppingAction().edep
        # Add up all energies in the volume.
        depEnergy = 0
        for i, name in enumerate(nameList):
            if name == volumeName:
                depEnergy += edep[i]

        return depEnergy/GeV
    #--------------------------------------------------------------------------

    def calo_readout(self):
        """Count the number of charged tracks in the active material.

        Count the number of charged particles crossing active layers of a
        calorimeter. First determine the start and the end point of the track.
        Next, use those points to calculate the number of crossed active
        layers for each track. Add up the result for all tracks. To insure
        correct functionality the volumes in the detector have to be numbered
        in increasing order and the active layers assigned odd numbers. The
        parameter for the world volume should be -1.

        :return:
           The number of charged tracks in all active layers.
        :rtype: int
        """
        # Set the counter number of tracks to zero.
        numOfTracks = 0
        # Get the charge and the volume number of the start and end point of
        # the track.
        tags = gRunManager.GetUserTrackingAction().preVolNum
        ends = gRunManager.GetUserTrackingAction().postVolNum
        charge = gRunManager.GetUserTrackingAction().charge
        # Get the detector construction class.
        readoutGeometry = gRunManager.GetUserDetectorConstruction()
        # A dictionary to translate the volume number of the active layer in
        # the entry number of the previously defined list.
        switch = {2*i+1 : i
                  for i in range(readoutGeometry.numOfActLayers)
        }
        toBeTracked = True

        # Loop over all start points of tracks.
        for i,tag in enumerate(tags):
            # Only charged particles are tracked.
            if charge[i] == 0:
                toBeTracked = False
            else:
                toBeTracked = True
            # Analyse the end point of the track.
            if toBeTracked:
                end = ends[i]
                # The origin of the track of the primary is set to the first
                # absorber layer.
                if tag == -1:
                    tag = 0
                diff = end - tag
                # Ensure positive diff values are counted.
                if diff < 0:
                    diff = -diff
                # Check if layer material of start and end point is different.
                if diff in switch:
                    # Add an layer to diff and calculate the number of active
                    # layers between start and end point.
                    numOfTracks += int((diff + 1) / 2)
                # Check if layer of start and end point is an active layer.
                elif tag in switch and end in switch:
                    # The number of crossed active layers is the half of all
                    # crossed layers plus the active layer the track starts
                    # or ends in.
                    numOfTracks += int(diff/2) + 1
                # Else the layer of start and end point is a passive layer.
                else:
                    # Calculate the number of crossed active layers.
                    numOfTracks += int(diff/2)

        return numOfTracks
    #--------------------------------------------------------------------------

    def get_charges(self):
        """Returns list of charges as a single list.

        If more than one event was simulated, they list is still one
        dimesional thus the information, which charge belongs to which event
        is not obvious.

        :return:
            The charges of all particles in a run.
        :rtype: list of int
        """
        charges = gRunManager.GetUserTrackingAction().charge
        return charges
    #--------------------------------------------------------------------------
    
    def get_step_energy_deposit(self):
        """Get location of energy deposition and energy deposited.

        The energy deposited at each step of the particle trajectories as well
        as the coordinates of the energy deposition are taken from the
        SteppingAction and converted to the input units.

        :return:
            Location in x,y,z of the energy depositions and amount deposited.
        :rtype:
            List of np.ndarray objects.
        """
        # Get the instance of the G4VUserDetectorConstruction class.
        readoutGeometry = gRunManager.GetUserDetectorConstruction()
        
        # Read the positions and energy deposits at each step.
        x_step = np.array(gRunManager.GetUserSteppingAction().xList)/cm + readoutGeometry.worldX/cm
        y_step = np.array(gRunManager.GetUserSteppingAction().yList)/cm
        z_step = np.array(gRunManager.GetUserSteppingAction().zList)/cm
        edep = np.array(gRunManager.GetUserSteppingAction().edep)/GeV
        return [x_step, y_step, z_step, edep]
    #--------------------------------------------------------------------------
    
    def get_first_interaction(self):
        """Get creation process of particles created from primary particle.
        
        :return:
            Names of processes that created particles from primary particle.
        :rtype:
            Set of str
        """
        processes = set(gRunManager.GetUserTrackingAction().proc_list)
        return processes
        
