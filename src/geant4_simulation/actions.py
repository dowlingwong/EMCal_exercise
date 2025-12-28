"""Provide the action classes and the primary generator.

Classes
-------

PrimaryGenerator : Generate primary particles and vertices.

RunAction : Reset the lists generated during a run.

TrackingAction : Fill informations of the tracks in lists.

SteppingAction : Fill informations of the steps in lists.
"""

__author__ = 'Maximilian Burkart'

from Geant4 import *

import geant4_simulation.geometry

class PrimaryGenerator(G4VUserPrimaryGeneratorAction):
    """Generate the primary particle and the primary vertex."""

    def __init__(self,
                 particleName = 'e-',
                 energy = 1.*GeV,
                 position = G4ThreeVector(-10.*cm,0,0),
                 momentumDirection = G4ThreeVector(1.,0.,0.),
                 numberOfParticles = 1):
        """Set the initial properties of the primary particle.

        Extend the constructor of the class ``G4VUserPrimaryGeneratorAction``
        by creating a particle gun instance. Set initial values for some
        parameters of the particle gun.

        Keyword arguments:

        particleName : string
            The string identifier of the primary particle.

            Default is e-.

        energy : double
            The kinetic energy of the primary particle in GeV.

            Default is 1 GeV.

        position : G4ThreeVector
            The starting point of the primary particle.

            Default is (-10 cm, 0, 0).

        momentumDirection : G4ThreeVector
            The direction of the momentum of the particle.

            Default is (1, 0, 0).

        numberOfParticles : int
            The number of particles shot at once.

            Default is 1.
        """
        G4VUserPrimaryGeneratorAction.__init__(self)
        # Create the particle gun.
        self.particleGun = G4ParticleGun(numberOfParticles)
        # Set the parameters of the primary particle.
        particleTable = gParticleTable.GetParticleTable()
        particle = particleTable.FindParticle(particleName)
        self.particleGun.SetParticleDefinition(particle)
        self.particleGun.SetParticleEnergy(energy)
        self.particleGun.SetParticlePosition(position)
        self.particleGun.SetParticleMomentumDirection(momentumDirection)

    def GeneratePrimaries(self, anEvent):
        """Generate the primary vertex.

        Parameters:

        anEvent : G4Event
            The event the primary vertex is assigned to.
        """
        self.particleGun.GeneratePrimaryVertex(anEvent)


class TrackingAction(G4UserTrackingAction):
    """Write information on the tracks in lists.

    The written data is used to analyse the simulated events. It contains
    information on the charge, vertex, track ID of the parent partcile and
    the volume numbers of the start and end point of the tracks.
    """

    def __init__(self):
        """Generate the lists the data is written in.

        Extends the constructor of the base class.
        """
        G4UserTrackingAction.__init__(self)
        self.preTrackIDList = []
        self.vertexList = []
        self.preVolNum = []
        self.postVolNum = []
        self.charge = []
        self.proc_list = []

    def PreUserTrackingAction(self, aTrack):
        """Get information on the tracked particle and the start point."""
        self.preTrackIDList.append(aTrack.GetParentID())
        # Get the x coordinate of the partilces origin.
        self.vertexList.append(aTrack.GetVertexPosition().getX())
        self.charge.append(aTrack.GetDefinition().GetPDGCharge())
        self.preVolNum.append(aTrack.GetVolume().GetCopyNo())
        # if aTrack.GetCreatorProcess() is not None:
        #     print(aTrack.GetCreatorProcess().GetProcessName())
        if aTrack.GetCreatorProcess() is not None and aTrack.GetParentID() == 1:
            self.proc_list.append(str(aTrack.GetCreatorProcess().GetProcessName()))


    def PostUserTrackingAction(self, aTrack):
        """Get the copy number of the volume the end point is in."""
        self.postVolNum.append(aTrack.GetVolume().GetCopyNo())


class SteppingAction(G4UserSteppingAction):
    """Create lists to store information on the energy deposit during a step.

    Lists for all coordinates of the step points, to store name of the
    volume and the deposited energy in this step are created. The coordinates
    and the deposited energy can be used to create histograms of the energy
    deposit. The volume name is used by the ``get_edep_in_volume()`` method.
    """

    def __init__(self):
        """Create the lists."""
        G4UserSteppingAction.__init__(self)
        self.xList = []
        self.yList = []
        self.zList = []
        self.edep = []
        self.geomNameList = []

    def UserSteppingAction(self, aStep):
        """Write the information in the lists."""
        # Get the position of the pre and post step points.
        preStep = aStep.GetPreStepPoint().GetPosition()
        postStep = aStep.GetPostStepPoint().GetPosition()
        # Use the mean value of the start and end point as the place
        # the energy deposited occurs.
        self.xList.append((preStep.getX() + postStep.getX())/2.)
        self.yList.append((preStep.getY()+postStep.getY())/2.)
        self.zList.append((preStep.getZ()+postStep.getZ())/2.)
        # Get the total energy deposited during a step.
        self.edep.append(aStep.GetTotalEnergyDeposit())
        self.geomNameList.append(str(aStep.GetTrack().GetVolume().GetName()))


class RunAction(G4UserRunAction):
    """Reset all lists at the beginning of a run."""

    def __init__(self, stepAct, trackAction):
        """Pass the SteppingAction and TrackingAction classes to RunAction."""
        G4UserRunAction.__init__(self)
        self.step = stepAct
        self.track = trackAction

    def BeginOfRunAction(self, aRun):
        """Reset all lists."""
        self.step.xList, self.step.yList, self.step.zList = [], [], []
        self.step.edep = []
        self.step.geomNameList = []
        self.track.preVolNum, self.track.postVolNum = [], []
        self.track.preTrackIDList, self.track.vertexList = [], []
        self.track.charge = []
        self.track.proc_list = []

    def GenerateRun(self):
        """Do nothing when generating a run."""

    def EndOfRunAction(self, aRun):
        """Do nothing when ending a run."""
