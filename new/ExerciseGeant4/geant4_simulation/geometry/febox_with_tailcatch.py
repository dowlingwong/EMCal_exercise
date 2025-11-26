__author__ = 'Maximilian Burkart'

from Geant4 import *
import geant4_simulation.materials as materials

class febox_with_tailcatch(G4VUserDetectorConstruction):
    """Create a volume for leakage studies.

    The volume consists of an iron box followed by a smaller lead box. The
    lead box is used to determine if a part of the energy of the incoming
    particle is not deposited in the iron box.

    :param float length:
       Length of the iron box in cm.

       Default is 20.

    :param float height:
       The y and z dimension of the box in cm.

       Default is 10.
    """

    def __init__(self, length=20., height=10.):
        """Set the instance variables to the given values.

        Extend the constructor of the base class."""
        G4VUserDetectorConstruction.__init__(self)
        self.worldX = length*cm+7.5*cm
        self.worldY = height*cm

    def Construct(self):
        """Construct the volumes.

        Return the physical world volume.
        """
        # All volumes have to be globals.
        global solidWorld, logicalWorld, physicalWorld
        global solidTarget, logicalTarget, physicalTarget
        global solidTailCatch, logicTailCatch

        # Set the z dimension of the volume.
        worldZ = self.worldY

        # Create the world volume.
        solidWorld = G4Box("World", self.worldX, self.worldY, worldZ)
        logicalWorld = G4LogicalVolume(solidWorld, materials.vac, "World")
        physicalWorld = G4PVPlacement(None,
                                       G4ThreeVector(),
                                       "World",
                                       logicalWorld,
                                       None,
                                       False,
                                       0)

        # Set the properties of the iron box.
        ironX = self.worldX - 7.5*cm
        ironY = self.worldY
        ironZ = worldZ

        # Create the physical volume of the box.
        solidTarget = G4Box("Target", ironX, ironY, ironZ)
        logicalTarget = G4LogicalVolume(solidTarget, materials.Fe, "Target")
        self.physicalTarget = G4PVPlacement(None,
                                            G4ThreeVector(-7.5*cm,0,0),
                                            "Target",
                                            logicalTarget,
                                            physicalWorld,
                                            False,
                                            0)

        solidTailCatch = G4Box("Tailcatcher", 5.*cm, ironY, ironZ)
        logicalTailCatch = G4LogicalVolume(solidTailCatch, materials.Pb,
                                           "Tailcatcher")
        G4PVPlacement(None,
                      G4ThreeVector(self.worldX - 5.*cm,0,0),
                      "Tailcatcher",
                      logicalTailCatch,
                      physicalWorld,
                      False,
                      0)

        # Set the tracking cut to the same values used in the compcalor
        # geometry and assign it to the iron box.
        trackCut = G4UserLimits(1.*cm, self.worldX+2,
                                2000*s, 0.5*MeV)
        logicalTarget.SetUserLimits(trackCut)

        # Return the physical volume.
        return physicalWorld

