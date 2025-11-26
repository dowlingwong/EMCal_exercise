__author__ = 'Maximilian Burkart'

from Geant4 import *
import geant4_simulation.materials as materials

class compcalor(G4VUserDetectorConstruction):
    """Construct a sampling calorimeter used for compensation studies.

    The calorimeter consists of passive iron layers and active scintillator
    layers. Its length is determined by the total length of iron that should
    be used. The number of layers is calculated from the given parameters.

    :param float absLen:
       Width of the absorber layer in cm.

       Default is 3.0.

    :param float actLen:
       Width of the active layer in cm.

       Default is 1.0.

    :param float feLen:
       Total amount of iron given in length in m.

       Default is 1.6.
    """
    def __init__(self, absLen=3., actLen=1., feLen=1.6):
        """Set the dimension of the calorimeter and the contained layers.

        Extend the constructor of the bass class by setting the half length
        of the world volume, the length of the layers and calculate the number
        of active layers and the total length of the calorimeter.
        """
        G4VUserDetectorConstruction.__init__(self)
        absLen = absLen*cm
        actLen = actLen*cm
        feLen *= 1.*m
        # Calculate the total length of the world volume.
        worldLen = feLen + actLen/absLen * feLen
        self.worldX = worldLen/2.

        self.lenOfAbsLayer = absLen
        self.lenOfActLayer = actLen
        self.numOfActLayers = int((worldLen-absLen)/(absLen+actLen))

        # Check if all calculations done so far are correct.
        self.calLen = (absLen + actLen) * self.numOfActLayers + absLen
        if self.calLen > 2 * self.worldX:
            print('Warning: Calorimeter is bigger than the world volume...')

    def Construct(self):
        """Construct the sampling calorimeter.

        Return the created physical world volume.
        """
        # All created volumes have to be globally avaiable.
        global solidWorld, logicWorld, physWorld
        global arBox, arUnit, pbBox, pbUnit

        worldY = self.worldX/2.
        # Create the world volume.
        solidWorld = G4Box("World", self.worldX, worldY, worldY)
        logicWorld = G4LogicalVolume(solidWorld, materials.vac, "World")
        # The copy number of the world volume is set to -1 to insure a
        # correct readout.
        physWorld = G4PVPlacement(None,
                                  G4ThreeVector(),
                                  "World",
                                  logicWorld,
                                  None,
                                  False,
                                  -1)

        # Convert the given layer lengths in half lengths. The constructed
        # solids now have the correct lengths.
        ironX = self.lenOfAbsLayer/2.
        scintX = self.lenOfActLayer/2.

        # Create the solids and logical volumes of the layers.
        scintBox = G4Box("scintBox", scintX, worldY, worldY)
        ironBox = G4Box("ironBox", ironX, worldY, worldY)
        scintUnit = G4LogicalVolume(scintBox, materials.scint, "logScint")
        ironUnit = G4LogicalVolume(ironBox, materials.Fe, "logIron")

        # Add user limits to the simulation. The only value that matters is
        # last. It is a tracking cut to speed up the simulation.
        trackCut = G4UserLimits(self.lenOfAbsLayer, self.worldX+2,
                                2000*s, 0.5*MeV)
        # The parameters of the G4UserLimits class are the maximum stepLength,
        # the maximum TrackLength, the maximum tracking time and the tracking
        # cut.
        # Assign the UserLimits to the logical volumes.
        scintUnit.SetUserLimits(trackCut)
        ironUnit.SetUserLimits(trackCut)

        # Set the differnce in position of two layers.
        push = ironX + scintX
        # Set first position of a layer.
        spot = -self.worldX + ironX

        # The volumes are numbered in increasing order starting at zero.
        # Passive layers get even numbers. The numbers of active layers
        # are odd.
        volNum = 0

        for i in range(self.numOfActLayers+1):
            # Place a passive layer.
            G4PVPlacement(None,
                          G4ThreeVector(spot, 0, 0),
                          "Iron",
                          ironUnit,
                          physWorld,
                          False,
                          volNum)
            # Update the position to place the next volume.
            spot += push
            volNum += 1

            if (i < self.numOfActLayers):
                # Place an active layer.
                G4PVPlacement(None,
                              G4ThreeVector(spot, 0, 0),
                              "scint",
                              scintUnit,
                              physWorld,
                              False,
                              volNum)

                spot += push
                volNum += 1

        # Return the world volume.
        return physWorld
