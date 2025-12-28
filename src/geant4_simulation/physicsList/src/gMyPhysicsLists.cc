// wrap the physics list classes with boost
#include <boost/python.hpp>
#include "MyQGSP_BERT.hh"
#include "TherapyPhysics.hh"
#include "EMPhysics.hh"


using namespace boost::python;

BOOST_PYTHON_MODULE(libphyslist)
{
    class_<MyQGSP_BERT, MyQGSP_BERT*, bases<QGSP_BERT>, boost::noncopyable >
    ("MyQGSP_BERT","physics list with steplimit support")
    ;
    
    class_<TherapyPhysics, TherapyPhysics*, bases<QGSP_BIC>, boost::noncopyable >
    ("TherapyPhysics","physics list for lower energies")
    ;

    class_<EMPhysics, EMPhysics*, bases<G4VModularPhysicsList>, boost::noncopyable >
    ("EMPhysics","physics list for lower energies")
    ;
}
