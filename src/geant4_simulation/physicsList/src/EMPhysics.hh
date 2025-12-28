#ifndef TestEMPhysics_h
#define TestEMPhysics_h 1

#include "globals.hh"
#include "G4VModularPhysicsList.hh"

class EMPhysics: public G4VModularPhysicsList
{
	public:
		EMPhysics(G4int ver = 1);
		virtual ~EMPhysics()=default;

		EMPhysics(const EMPhysics&)=delete;
		EMPhysics& operator=(const EMPhysics&)=delete;
};

#endif
