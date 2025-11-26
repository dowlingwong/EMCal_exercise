__author__ = 'Maximilian Burkart'

from Geant4 import *
import geant4_simulation.materials as materials


class samplingcalo(G4VUserDetectorConstruction):
    """Define a sampling calorimeter made of lead and liquid argon layers.

    The width of the absorber, the active layers and the number of layers
    may be set by the user. The length of the calorimeter is calculated from
    these values.

    :param float absLen:
       Width of the absorber layer in cm.

       Default is 2.

    :param float actLen:
       Width of the active layer in cm.

       Default is 1.

    :param int layerNum:
       Number of active layers in the calorimeter.

       Default is 16.
"""

    def __init__(self, absLen=2., actLen=1., layerNum=16):
        """Set the prperties of the calorimeter.

        Extend the constructor of the base class by setting the the
        instance variables to the given values.
        """
        G4VUserDetectorConstruction.__init__(self)
        # Calculate the length of the world volume.
        worldLen = (absLen*1.*cm + actLen*1.*cm)*layerNum + absLen*1.*cm
        # The boundaries of the world volume range from -worldLen/2 to
        # worldLen/2.
        self.worldX = worldLen/2.
        self.lenOfAbsLayer = absLen*1.*cm
        self.lenOfActLayer = actLen*1.*cm
        self.numOfActLayers = layerNum
        self.calLen = ((self.lenOfAbsLayer + self.lenOfActLayer) * layerNum
                       + self.lenOfAbsLayer)
        # Check if the calculations were correct.
        if self.calLen > 2 * self.worldX:
            print('Warning: Calorimeter is bigger than the world volume...')

    def Construct(self):
        """Construct the calorimeter.

        Returns:

        physWorld : G4PhysicalVolume
            The constructed physical world volume.
        """

        # Define global accesible volumes.
        global solidWorld, logicWorld, physWorld
        global arBox, arUnit, pbBox, pbUnit

        # Set the half heights of the world volume.
        worldY = 10.*cm
        worldZ = 10.*cm

        # Create, fill and place the world volume.
        solidWorld = G4Box("World", self.worldX, worldY, worldZ)
        logicWorld = G4LogicalVolume(solidWorld, materials.vac, "World")
        physWorld = G4PVPlacement(None, G4ThreeVector(), "World", logicWorld,
                                  None, False, -1)

        # Set the half widths of the layers.
        leadX = self.lenOfAbsLayer/2.
        arX = self.lenOfActLayer/2.

        # Create the boxes and logical volumes.
        arBox = G4Box("argonBox", arX, worldY, worldZ)
        pbBox = G4Box("leadBox", leadX, worldY, worldZ)
        arUnit = G4LogicalVolume(arBox, materials.liquidAr, "logAr")
        pbUnit = G4LogicalVolume(pbBox, materials.Pb, "logLead")

        # Set the length between the position of two layers.
        push = leadX + arX
        # Set the starting point of the positioning.
        spot = -self.worldX - arX

        # Set the volume number of the primary layer to zero.
        volNum = 0

        # Position the volumes and numerate them in increasing order.
        for i in range(self.numOfActLayers+1):
            spot += push
            G4PVPlacement(None, G4ThreeVector(spot, 0, 0), "Lead", pbUnit,
                          physWorld, False, volNum)
            volNum += 1
            if (i < self.numOfActLayers):
                spot += push
                G4PVPlacement(None, G4ThreeVector(spot, 0, 0), "Ar",
                              arUnit, physWorld, False, volNum)
                volNum += 1

        return physWorld

