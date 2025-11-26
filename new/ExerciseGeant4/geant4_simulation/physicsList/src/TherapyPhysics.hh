//Header File of the class TherapyPhysics
//implementing the physics used in the simulation of a tumor therapy
//

#ifndef TherapyPhysics_h
#define TherapyPhysics_h 1
#include "G4VModularPhysicsList.hh"
#include "globals.hh"
#include "QGSP_BIC.hh"


class G4VPhysicsConstructor;

class TherapyPhysics : public QGSP_BIC
{
public:
    //Konstruktor
    TherapyPhysics(G4int verbose = 1);
    
    //Destruktor
    virtual ~TherapyPhysics();
    
    //member functions
    virtual void SetCuts();
    
private:
    
};



#endif
