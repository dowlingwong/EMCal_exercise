"""Create the materials used in the geometries.

This module provides the materials being used by the geometries.
These materials can also be used to define new ``G4VUserDetectorConstruction``
classes. The properties of materials not created through the ``gNistManager``
instance are taken from the review *Atomic and Nuclear properties of materials*
provided by the Particle Data Group.[Pat16]_ All available materials are listed
below.

vac : G4Material
   The representation of the vacuum.

air : G4Material
   The representation of air at standard conditions.

water : G4Material
    The representation of water.

Pb : G4Material
    The representation of lead.

Fe : G4Material
    The representation of iron.

liquidAr : G4Material
    The representation of liquid argon for use in calorimeters.

scint : G4Material
    The scintillator material used in the compensating calorimeter.
    The properties of this material are copied from the old application.

pet : G4Material
    The representation of polyethylene.

bone : G4Material
    The bone material used to build the skull.

.. [Pat16] Patrigiani, C. et al (Particle Data Group): 2016 Review
           of Particle Physics. Chinese Physics C, 40(10001), 2016.
           avaiable at:
           www-pdg.lbl.gov/2016/reviews/
           rpp2016-rev-atomic-nuclear-prop.pdf
"""

__author__ = 'Maximilian Burkart'

from Geant4 import *

# Declare the generated materials as global avaiable.
global air, Pb, liquidAr, Fe, water, vac, pet, scint, bone
# Create the materials via the NistManager
air = gNistManager.FindOrBuildMaterial("G4_AIR")
water = gNistManager.FindOrBuildMaterial("G4_WATER")
vac = gNistManager.FindOrBuildMaterial("G4_Galactic")
bone = gNistManager.FindOrBuildMaterial("G4_B-100_BONE")
# Create the elements used in compound materials by specifying the atomic
# and the mass number.
a = 1.008*g/mole
elH = G4Element("Hydrogen", "H", 1., a)
a = 12.0107*g/mole
elC = G4Element("Carbon", "C", 6., a)
a = 35.453*g/mole
elCl = G4Element("Chlor", "Cl", 17., a)
# Create the materials by explicitely specifying the properties. The 
# properties of the material are given before the actual definition.
# z = atomic number
# a = mass number
# Create lead.
materialName = "Lead"
z = 82.
a = 207.2*g/mole
density = 11.350*g/cm3
Pb = G4Material(materialName, z, a, density)
# Create liquid argon.
materialName = "liquidArgon"
z = 18.
a = 39.948*g/mole
density = 1.396*g/cm3
liquidAr = G4Material(materialName, z, a, density)
# Create polyethylene.
density = 0.89*g/cm3        #specific gravity value
pet = G4Material("Polyethylene", density, 2)
pet.AddElement(elH, 0.143711)
pet.AddElement(elC, 0.856289)
# Create iron.
materialName = "Iron"
z = 26.
a = 55.845*g/mole
density = 7.874*g/cm3
Fe = G4Material(materialName, z, a, density)
# Create the scintillator. The values are taken from the old exercise.
materialName = "Scintillator"
z = 1.
a = 1.847*g/mole
density = 1.032*g/cm3
scint = G4Material(materialName, z, a, density)
