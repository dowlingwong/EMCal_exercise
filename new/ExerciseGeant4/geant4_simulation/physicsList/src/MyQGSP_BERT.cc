//src file of the class MyQGSP_BERT, creating the physics list
//
//add the G4StepLimiterPhysics constructor to the physics list QGSP_BERT
//and change the neutron cut on the kinetic energy to 0.5 GeV
#include "MyQGSP_BERT.hh"

#include <iomanip>

#include "globals.hh"
#include "G4SystemOfUnits.hh"

#include "G4StepLimiterPhysics.hh"
#include "G4VPhysicsConstructor.hh"
#include "G4NeutronTrackingCut.hh"
#include "G4ProductionCutsTable.hh"
#include "G4UserSpecialCuts.hh"
#include "G4SpecialCuts.hh"

//Konstruktor
MyQGSP_BERT::MyQGSP_BERT(G4int verbose) : QGSP_BERT(verbose)
{
    G4NeutronTrackingCut* neuCut = new G4NeutronTrackingCut(verbose);
    neuCut->SetKineticEnergyLimit(0.5*MeV);
    this->RegisterPhysics(neuCut);
    G4cout << "###Changing the neutron cuts of the physicslist..." << G4endl << G4endl;
    
    // add the step limiter physics
    this->RegisterPhysics(new G4StepLimiterPhysics(verbose));
    G4cout << "###Adding step limiter physics to the Geant4 simulation engine..." << G4endl << G4endl;
}

//Destruktor
MyQGSP_BERT::~MyQGSP_BERT()
{
}

void MyQGSP_BERT::SetCuts()
{
    QGSP_BERT::SetCuts();
}

