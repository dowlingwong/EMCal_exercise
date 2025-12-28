//Implementation file of the class TherapyPhysics
//a phyisics list derived from QGSP_BIC
//suitable for applications with energies lower than 1 GeV
//

#include "TherapyPhysics.hh"

#include <iomanip>
#include "G4ios.hh"
#include "G4ProcessManager.hh"
#include "G4ProcessVector.hh"
#include "G4ParticleTypes.hh"
#include "G4ParticleTable.hh"
#include "G4Material.hh"
#include "G4MaterialTable.hh"


#include "globals.hh"
#include "G4SystemOfUnits.hh"

#include "QGSP_BIC.hh"
#include "G4StepLimiterPhysics.hh"


TherapyPhysics::TherapyPhysics(G4int verbose) : QGSP_BIC(verbose)
{
    G4cout << "###Adding step limiter physics to the list..." << G4endl << G4endl;
    this->RegisterPhysics(new G4StepLimiterPhysics(verbose));
}

TherapyPhysics::~TherapyPhysics()
{
}

void TherapyPhysics::SetCuts()
{
    QGSP_BIC::SetCuts();
}
