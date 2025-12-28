"""Define the class example_geometry inherited from the base class
G4VUserDetectorConstruction. The class has to provide the method Construct()
invoked by the RunManager to build the detector volume.
"""

__author__ = 'Maximilian Burkart'


# Import the necessary objects into the local namespace.
from Geant4 import *
# Import the material definitions.
import geant4_simulation.materials as materials


class example_geometry(G4VUserDetectorConstruction):
    """A simple geometry example geometry.

    This example geometry introduces the first user to the Geant4 way of
    defining geometries.

    :param float halfX:
       Half length of the created box in cm. The created box ranges from
       -halfX to halfX.

       Default is 20.
    """
    # Construct a simple example geometry containing an absorber. It should
    # be the starting point for building your own geometry. When building your
    # own geometry take care that the name of the class and the file match.
    def __init__(self, halfX=20.):
        """Set the length of the world volume representing the experimental hall.
        This length must be provided in order to set the origin of the
        primary particle to the correct position"""

        # First call the inherited constructor.
        G4VUserDetectorConstruction.__init__(self)

        # Set the half length of the world volume, respectively the experimental
        # hall. Keep in mind that this is only the half length of the actual
        # volume. If no unit is provided the length is interpreted in mm.
        self.worldX = halfX*cm

    def Construct(self):
        """Define all volumes the detector should contain. The return value of
        this function should be the generated detector volume. The
        definition of a geometry is done in three steps. First the shape of
        the volume has to be defined, afterwards the volume has to be filled
        with a material. The solid now becomes a LogicalVolume. At the last
        step the volume has to be placed.The placed volume is called physical
        volume.
        """

        # First of all the volume containing the whole detector has to be
        # defined.
        # This volume is usually called the world volume.

        # Define the y and z lengths of the world volume.
        worldY, worldZ = 15.*cm, 15.*cm

        # The elements of the geometry are used by the simulation engine.
        # Therefore the solids, logical volumes and the physical world volume
        # have to be global.
        global solidWorld, logicWorld, physWorld
        global solidTarget, logicTarget

        # Build the solid world volume. The easiest shape of theworld volume
        # is a box.
        solidWorld = G4Box("World",self.worldX,worldY,worldZ)
        # The siganture of G4Box is G4Box(name,halfx,halfy,halfz),
        # where halfx is the half length of the box.
        # Fill the world volume with vacuum.
        logicWorld = G4LogicalVolume(solidWorld, materials.vac, "World")
        # The first argument is specifying the solid the logical volume is
        # build of. The second argument gives the material of the volume and
        # the third is the name of the volume.
        logicWorld.SetVisAttributes(G4VisAttributes(G4Color(*[1.,1.,1.,0.1])))

        # Now place the volume.
        physWorld = G4PVPlacement(None,
                                  G4ThreeVector(),
                                  logicWorld,
                                  "World",
                                  None,
                                  False,
                                  0)
        # The object G4PVPlacement is called with the following arguments
        # G4PVPlacement(rotation matrix ->ususally not needed in our case,
        #               a G4ThreeVector object specifying the position of
        #               the volume relative to the mother volume,
        #               logical volume to be placed,
        #               name of the placed volume,
        #               mother logical volume,
        #               boolean operation having no use at all,
        #               the copy number of the volume)

        # Set the length of the lead box to a value 10cm less than the world.
        leadX = self.worldX - 5.*cm

        # Define the three volumes for the lead box.
        solidTarget = G4Box("Target",leadX,worldY,worldZ)
        logicTarget = G4LogicalVolume(solidTarget,materials.Pb, "Target")
        # Place the target in the physical world.
        G4PVPlacement(None,
                      G4ThreeVector(5.*cm,0,0),
                      logicTarget,
                      "Target",
                      logicWorld,
                      False,
                      0)

        # Add special physics to the logical volume(s).
        # This needs to be done if one wants to speed up the simulation with
        # additional cuts or to improve the accuracy of the simulation with
        # regards to the deposited energy through step limitations.
        maxStep = 20.*cm
        maxTrackLen = 2 * self.worldX
        maxTime = 5*s
        minEkin = 1.*GeV
        # These values are only arbitrary. Set your own values depending
        # on your simulation.

        # specialPhys = G4UserLimits(maxStep,maxTrackLen,maxTime,minEkin)
        # logicTarget.SetUserLimits(specialPhys)
        logicTarget.SetVisAttributes(G4VisAttributes(G4Color(*[0,0,1,0.4])))


        # Return the physical world.
        return physWorld
