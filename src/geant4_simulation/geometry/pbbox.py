__author__ = 'Maximilian Burkart'

from Geant4 import *
import geant4_simulation.materials as materials

class pbbox(G4VUserDetectorConstruction):
    """Create a simple lead box to simulate elementary interactions.

    The material of the box can be changed to iron via the
    :meth:`~geant4_10_5_package.change_material` method of the
    :class:`ApplicationManager` class.

    :param float length:
       Length of the lead box in cm.

       Default is 20.

    :param float height:
       Height and width of the lead box.

       Default is 10.
    """

    def __init__(self, length=20., height=10.):
        """Set the instance variables to the given parameters."""
        G4VUserDetectorConstruction.__init__(self)
        self.worldX = length/2.*cm
        self.worldY = height/2.*cm
        # Set a step limitation to insure correct readout of the placed
        # energy.
        self.stepLimit = G4UserLimits(4.*mm)

    def Construct(self):
        """Construct the physical world volume containing the lead box."""
        # All created volumes have to be globals.
        global solidWorld, logicalWorld, physicalWorld
        global solidTarget, logicalTarget, physicalTarget
        # Set the width.
        worldZ = self.worldY
        # Create the solid representation of the world volume.
        solidWorld = G4Box("World", self.worldX, self.worldY, worldZ)
        # Create the logical_world volume via
        # G4LogicalVolume(solid, material, name).
        logicalWorld = G4LogicalVolume(solidWorld, materials.vac, "World")
        # Create the physical world volume via the G4PVPlacement method.
        # G4PVPlacement(rotation, position, name, logical volume,
        #               mother volume, boolean operations, copy number)
        physicalWorld = G4PVPlacement(None,
                                       G4ThreeVector(),
                                       "World",
                                       logicalWorld,
                                       None,
                                       False,
                                       0)
        # Set the properties of the lead box.
        leadX = self.worldX
        leadY = self.worldY
        leadZ = worldZ
        # Create and place the box.
        solidTarget = G4Box("Target", leadX, leadY, leadZ)
        logicalTarget = G4LogicalVolume(solidTarget, materials.Pb, "Target")
        self.physicalTarget = G4PVPlacement(None,
                                            G4ThreeVector(),
                                            "Target",
                                            logicalTarget,
                                            physicalWorld,
                                            False,
                                            0)
        # Assign the step limit to the logical target volume.
        logicalTarget.SetUserLimits(self.stepLimit)
        
        # Return the physical volume.
        return physicalWorld
