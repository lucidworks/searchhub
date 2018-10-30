#!/bin/bash
echo "post ssh"

FUSION_HOME=${FUSION_HOME}/4.1.0
#SEARCHHUB_HOME=${SEARCHHUB_HOME}
#USERNAME=${USERNAME}
#DATA_SOURCES=${DATA_SOURCES}
#WIPE_OLD_INSTALL=${WIPE_OLD_INSTALL}

echo ${FUSION_HOME}
echo ${SEARCHHUB_HOME}
echo ${USERNAME}


echo "Downloading and installing additional required packages"
sudo apt-get -qq update
sudo apt-get -y -qq install gradle
sudo apt-get -y -qq install maven
sudo apt-get -y -qq install scala
sudo apt-get -y -qq install default-jdk
sudo apt-get -y -qq install zip
echo ""
echo ""

if [ ${WIPE_OLD_INSTALL} == 1 ]; then
    echo "Stopping Fusion services"
    ${FUSION_HOME}/bin/fusion stop
    echo ""
    echo ""

    echo "Removing old Fusion install"
    rm -r ${FUSION_HOME}
    echo ""
fi

# TODO: allow for building fusion directly from source on a chosen branch

# TODO: allow for command-line choice of what Fusion to download
if [ ! -e "/home/${USERNAME}/fusion-4.1.0.tar.gz" ]; then
  echo "Fusion file not found, downloading!"
  wget https://download.lucidworks.com/fusion-4.1.0/fusion-4.1.0.tar.gz
fi
echo "Fusion downloaded"
echo ""

echo "Extracting Fusion 4.1.0"
tar -C /home/ubuntu/ -x -f ./fusion-4.1.0.tar.gz
echo ""
echo ""

echo "Editing config files"
mv fusion.properties ${FUSION_HOME}/conf
mkdir ~/.fusion
mv license.properties ~/.fusion
mkdir ~/.m2
mv settings.xml ~/.m2
echo ""
echo ""

echo "launching Fusion"
${FUSION_HOME}/bin/fusion start
echo ""
echo ""

echo "Removing old SearchHub install"
rm -r ${SEARCHHUB_HOME} 
echo ""
echo ""

echo "Downloading SearchHub"
mkdir -p ${SEARCHHUB_HOME}
cd ${SEARCHHUB_HOME}
git clone https://github.com/lucidworks/searchhub.git
SEARCHHUB_HOME=${SEARCHHUB_HOME}/searchhub
cd ${SEARCHHUB_HOME}
git fetch origin
# TODO: allow for command-line choice of what branch to build from
git checkout -t origin/4_1_upgrade
echo ""
echo ""

echo "Moving SearchHub config files"
mv ~/myenv.sh.tmpl myenv.sh
mv ~/password_file.json.tmpl password_file.json
source myenv.sh
echo ""
echo ""

echo "Installing SearchHub"
./gradlew deployLibs --stacktrace
${FUSION_HOME}/bin/api restart
${FUSION_HOME}/bin/connectors restart
./install.sh
echo ""
echo ""

echo "Installation Complete!"

#delete settings.xml
rm -f ~/.m2/settings.xml

if [[ ! ${DATA_SOURCES} == "" ]]; then
    echo "Indexing datasources"
    ~/index_searchhub_datasources.sh -d ${DATA_SOURCES}
else
    echo "Not turning on any datasources, since you didn't ask for any.  Do that through the Fusion UI at this point"
fi
