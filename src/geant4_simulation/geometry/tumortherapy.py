__author__ = 'Maximilian Burkart'


from Geant4 import *
import geant4_simulation.materials as materials


class tumortherapy(G4VUserDetectorConstruction):
    """Construct the geometry used for studies on radiation therapy.

    The geometry represents the head of a patient. It consists of a spherical
    shell made out of the bone material. Inside this shell are two
    water-filled spheres. The bigger one represents the brain of the patient
    and the small one the tumor.
    """

    def __init__(self):
        """Set the properties of the world volume."""
        G4VUserDetectorConstruction.__init__(self)
        self.worldX = 10.*cm
        self.worldY = 10.*cm
        self.stepLimit = G4UserLimits(2.*mm)

    def Construct(self):
        """Construct the geometry."""
        # The constructed volumes have to be globals.
        global solidWorld, logicWorld, physWorld
        global solidSkull, logicSkull, solidBrain, logicBrain
        global solidTumor, logicTumor
        # Create the world volume.
        solidWorld = G4Box("World", self.worldX, self.worldY, self.worldY)
        logicWorld = G4LogicalVolume(solidWorld, materials.air, "World")
        physWorld = G4PVPlacement(None,
                                  G4ThreeVector(),
                                  "World",
                                  logicWorld,
                                  None,
                                  False,
                                  0)
        # Define the properties of the geometrical bodies. The radius of the
        # spherical shell ranges from 6 cm to 7 cm.
        solidSkull = G4Sphere("Skull",6.*cm, 7.*cm, 0*degree, 360*degree,
                              0*degree, 180*degree)
        solidBrain = G4Orb("Brain", 6.*cm)
        solidTumor = G4Orb("Tumor", 0.5*cm)
        # Create the logical volumes.
        logicSkull = G4LogicalVolume(solidSkull,
                                     materials.bone,
                                     "Skull")
        logicBrain = G4LogicalVolume(solidBrain, materials.water,
                                     "Brain")
        logicTumor = G4LogicalVolume(solidTumor, materials.water,
                                     "Tumor")
        # Create the physical volumes by placing the logical ones.
        G4PVPlacement(None, G4ThreeVector(), logicSkull, "Skull",
                      logicWorld, False, 0)
        G4PVPlacement(None, G4ThreeVector(), logicBrain, "Brain",
                      logicWorld, False, 0)
        G4PVPlacement(None, G4ThreeVector(-2.5*cm,0,0), logicTumor,
                      "Tumor", logicBrain, False, 0)
        # Assign the step limits to the logical volumes. To make the
        # position of the energy deposition more precise the step limit is
        # decreased in the tumor.
        logicSkull.SetUserLimits(self.stepLimit)
        logicBrain.SetUserLimits(self.stepLimit)
        stepLimit2 = G4UserLimits(0.5*mm)
        logicTumor.SetUserLimits(stepLimit2)

        # Return the physical world volume.
        return physWorld

