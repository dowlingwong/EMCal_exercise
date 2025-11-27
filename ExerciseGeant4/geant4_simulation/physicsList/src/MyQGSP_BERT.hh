// Header file of the class MyQGSP_BERT.
// This class inherits from the reference physics list QGSP_BERT. It
// adds an interface for the G4UserLimits class and a tracking cut for
// neutrons.
#ifndef MyQGSP_BERT_h
#define MyQGSP_BERT_h 1

#include "QGSP_BERT.hh"
#include "globals.hh"


class MyQGSP_BERT : public QGSP_BERT
{
public:
    //Konstruktor
    MyQGSP_BERT(G4int verbose = 1);
    
    //Destruktor
    virtual ~MyQGSP_BERT();
    
    //member function
    virtual void SetCuts();
    
private:
    
};

#endif
