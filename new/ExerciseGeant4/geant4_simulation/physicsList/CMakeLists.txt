#cmake file to build the physics list
cmake_minimum_required(VERSION 2.8)
project(physlist)

find_package(PythonLibs 2.7 REQUIRED)
include_directories(${PYTHON_INCLUDE_DIRS})

find_package(Boost 1.58.0 COMPONENTS python)
include_directories(${Boost_INCLUDE_DIRS})

find_package(Geant4 REQUIRED)
#Geant4_DIR="/home/ubuntuuser/geant4_exercise/geant4.10.3-install/bin/"
include_directories(${Geant4_INCLUDE_DIR})

#link_directories(${GEANT4_LIBRARY_DIR} ${Boost_LIBRARY_DIRS})
add_library(physlist SHARED 
            src/MyQGSP_BERT.hh
            src/MyQGSP_BERT.cc
            src/TherapyPhysics.hh
            src/TherapyPhysics.cc
            src/gMyQGSP_BERT.cc
            )

target_link_libraries(physlist ${Geant4_LIBRARIES} boost_python ${PYTHON_LIBRARIES} ${Boost_LIBRARIES})

install(TARGETS physlist DESTINATION /home/ununtuuser/geant4_exercise/geant4_10_5_package/)
