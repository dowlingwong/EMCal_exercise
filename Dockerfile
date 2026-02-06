FROM jeppelt/etp_tp:latest

USER root

### Install packages necessary to run Geant4
RUN apt-get -y update \
    && apt-get -y upgrade \
    && apt-get -y install \
	cmake \
	gcc \
	g++ \
	#python-dev \
	libxmu-dev \
	libgl1-mesa-dev \
	libboost-python-dev \
	libxerces-c-dev \
	libexpat1 \
	libx11-dev \
	libglu1-mesa-dev \
	freeglut3-dev \
	mesa-common-dev \
        imagemagick \
        gv \
    && apt-get -qq -y autoclean \
    && apt-get -qq -y autoremove \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

### Install Geant4
RUN conda install -c conda-forge  geant4 

#RUN mkdir geant4-source \
#    && SDIR=$(readlink -f geant4-source) \
#    && wget -q -O - http://cern.ch/geant4-data/releases/geant4.11.1.1.tar.gz | tar xzf - -C "geant4-source" \
#    && mkdir geant4-build && pushd geant4-build \
#    && cmake -DCMAKE_INSTALL_PREFIX=/opt/geant4 \
#             -DGEANT4_INSTALL_EXAMPLES=OFF \
#	     -DGEANT4_USE_OPENGL_X11=ON \
#	     -DGEANT4_USE_PYTHON=ON \
#	     -DGEANT4_INSTALL_DATA=OFF \
#	     ${SDIR}/geant4.11.1.1.p02 \
#    && make -j4 && make install \
#    && popd \
#    && rm -rf geant4-source geant4-build

ENV PYTHONPATH=$PYTHONPATH:/opt/geant4/lib/python3.9/site-packages \
    PATH=/opt/geant4/bin:$PATH \
    G4NEUTRONHPDATA=/data_share/tp1_Geant/share/Geant4-11.1.1./data/G4NDL4.6 \
    G4LEDATA=/data_share/tp1_Geant/share/Geant4-11.1.1./data/G4EMLOW7.9.1 \
    G4LEVELGAMMADATA=/data_share/tp1_Geant/share/Geant4-11.1.1./data/PhotonEvaporation5.5 \
    G4RADIOACTIVEDATA=/data_share/tp1_Geant/share/Geant4-11.1.1./data/RadioactiveDecay5.4 \
    G4PARTICLEXSDATA=/data_share/tp1_Geant/share/Geant4-11.1.1./data/G4PARTICLEXS2.1 \
    G4PIIDATA=/data_share/tp1_Geant/share/Geant4-11.1.1./data/G4PII1.3 \
    G4REALSURFACEDATA=/data_share/tp1_Geant/share/Geant4-11.1.1./data/RealSurface2.1.1 \
    G4SAIDXSDATA=/data_share/tp1_Geant/share/Geant4-11.1.1./data/G4SAIDDATA2.0 \
    G4ABLADATA=/data_share/tp1_Geant/share/Geant4-11.1.1./data/G4ABLA3.1 \
    G4INCLDATA=/data_share/tp1_Geant/share/Geant4-11.1.1./data/G4INCL1.0 \
    G4ENSDFSTATEDATA=/data_share/tp1_Geant/share/Geant4-11.1.1./data/G4ENSDFSTATE2.2 \
    G4DAWNFILE_VIEWER=NONE

RUN echo /opt/geant4/lib/ > /etc/ld.so.conf.d/extra.conf && ldconfig

### Install DAWN for visualisation of detector simulation
RUN mkdir dawn-source \
    && wget -q -O - http://geant4.kek.jp/~tanaka/src/dawn_3_91a.tgz | tar xzf - -C "dawn-source" \
    && export DAWN_PS_PREVIEWER=NONE && pushd dawn-source/dawn_3_91a \
    && make clean && make guiclean && make && make install \
    && popd && rm -rf "dawn-source"

### Set dawn environment variable to get only one output file from dawn.
### This prevents multiple files being written and fixes the name of the 
### output file the visualisation relies on.
ENV G4DAWNFILE_MAX_FILE_NUM=1

ENV PATH="/usr/bin:$PATH"

USER $NB_USER
