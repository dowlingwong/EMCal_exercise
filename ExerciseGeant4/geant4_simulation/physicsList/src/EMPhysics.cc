#include <iomanip>
// #include <CHLEP/Units/SystemOfUnits.h>

#include "globals.hh"

#include "G4EmStandardPhysics.hh"

#include "EMPhysics.hh"

EMPhysics::EMPhysics(G4int ver)
{
	G4cout << "<<< Geant4 Physics List simulation engine: EMPhysics" << G4endl;
	G4cout << G4endl;

	//defaultCutValue = 0.7*CLHEP::mm;
	SetVerboseLevel(ver);

	// EM Physics
	RegisterPhysics( new G4EmStandardPhysics(ver));
}
