#!/bin/bash

echo "Uploading config files"
echo "Fusion home:"${FUSION_HOME}
echo "SearchHub home:"${SEARCHHUB_HOME}
echo "Username:"${USERNAME}
echo "Hostname:"${SSH_HOSTNAME}
echo "Identity:"${IDENTITY_FILE}
echo "license.properties:" ${FUSION_LICENSE}
echo "settings.xml:" ${TWIGKIT_CREDENTIALS}
echo ""

scp -i ${IDENTITY_FILE} ${INSTALLER_HOME}/scripts/fusion_installer.sh ${USERNAME}@${SSH_HOSTNAME}:
scp -i ${IDENTITY_FILE} ${INSTALLER_HOME}/scripts/index_searchhub_datasources.sh ${USERNAME}@${SSH_HOSTNAME}:
scp -i ${IDENTITY_FILE} ${INSTALLER_HOME}/conf/fusion.properties ${USERNAME}@${SSH_HOSTNAME}:
scp -i ${IDENTITY_FILE} ${INSTALLER_HOME}/conf/myenv.sh.tmpl ${USERNAME}@${SSH_HOSTNAME}:
scp -i ${IDENTITY_FILE} ${INSTALLER_HOME}/conf/password_file.json.tmpl ${USERNAME}@${SSH_HOSTNAME}:
scp -i ${IDENTITY_FILE} ${FUSION_LICENSE} ${USERNAME}@${SSH_HOSTNAME}:license.properties
scp -i ${IDENTITY_FILE} ${TWIGKIT_CREDENTIALS} ${USERNAME}@${SSH_HOSTNAME}:

echo "Upload complete"
echo ""
