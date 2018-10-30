#!/bin/bash

unset FUSION_HOME
INSTALLER_HOME="$(dirname -- "${BASH_SOURCE-$0}")"
USERNAME="ubuntu"
DATA_SOURCES=""
TWIGKIT_CREDENTIALS=~/.m2/setting.xml
FUSION_LICENSE=""
WIPE_OLD_INSTALL=0

if [ $# == 0 ]; then
    echo "missing options, please use -h or --help to see all available options"
    exit 1
fi

function print_usage() {
    ERROR_MSG="$1"

    if [ "$ERROR_MSG" != "" ]; then
        echo -e "\nERROR: $ERROR_MSG\n"
    fi

    echo "Usage: install_fusion.sh [-d Datasources] [-f Fusion home] [-h Help] -H Hostname [-l Fusion license]"
	echo "                        -i SSH key [-s SearchHub home] [-t Twigkit credentials] [-u Username]"
	echo ""
    echo "Used for the creation of Fusion services utilizing searchhub with AWS services"
    echo ""
	echo "  -d|--datasource-list [comma-separated-list]"
	echo "                                  input a comma separated list of datasources to index"
	echo "  -f|--fusion_home [PATH]"
	echo "                                  Set desired Fusion home directory, if not set"
	echo "                                  this will default to: /home/<username>/fusion/4.1.0"
	echo "  -h|--help"
	echo "                                  Displays help"
	echo "  -H|--hostname [HOSTNAME]"
	echo "                                  Set the hostname of the remote instance to install the demo on" 
	echo "  -l|--fusion-license [PATH]"
	echo "                                  Set the path to license.properties for fusion licensing."
	echo "                                  Exclude this option if you plan on uploading it manually (although you may not be able to use the --datasource-list in this case)."
	echo "  -i|--identity [IDENTITY FILE PATH]"
	echo "                                  Set the identity file or key that will be used for SSH and SCP protocols"
	echo "  -s|--searchhub_home [PATH]"
	echo "                                  Set desired SearchHub home directory, if not set"
	echo "                                  this will default to: /home/<username>/src/lucidworks/searchhub"
	echo "  -t|--twigkit_credentials [PATH]"
	echo "                                  Set the path to the (maven) settings.xml file that gradle will use when building searchhub. Defaults to .m2/settings.xml"
	echo "  -u|--username [USERNAME]"
	echo "                                  Set the username that will be used for SSH and SCP protocalls,"
	echo "                                  as well as Fusion/SearchHub home directories. This will default"
	echo "                                  to: ubuntu"
    echo ""
    echo "The hostname, username, and indentity_file flags are required due to the dependancies of SSH and SCP,"
    echo "otherwise all other flags have default variables set."
    echo ""
    echo "Examples: ./install_fusion.sh -i ~/.ssh/foobar.pem -H ec2-11-111-111-111.compute-1.amazonaws.com"
    echo "          ./install_fusion.sh --identity ~/.ssh/foobar.pem --username ubuntu --hostname ec2-11-111-111-111.compute-1.amazonaws.com"
    echo "          ./install_fusion.sh -i ~/.ssh/foobar.pem -u ubuntu -H ec2-11-111-111-111.compute-1.amazonaws.com -f /tmp/fusion/4.1.0 -s /home/ubuntu/src/lucidworks/searchhub"
    echo "          ./install_fusion.sh -i ~/.ssh/foobar.pem -H ec2-11-111-111-111.compute-1.amazonaws.com -l ~/Documents/foo/license.properties -t ~/Documents/foo/settings.xml"
}

#options
if [ $# -gt 0 ]; then
    while true; do
        case "$1" in
            -d|--datasource-list)
                if [[ -z "$2" || "${2:0:1}" == "-" ]]; then
                    print_usage "a list of datasources is required when using the $1 option!"
                    exit 1
                fi
                DATA_SOURCES=${2}
                shift 2
            ;;
            -f|--fusion_home)
                if [[ -z "$2" || "${2:0:1}" == "-" ]]; then
                    print_usage "path for fusion home is required when using the $1 option!"
                    exit 1
                fi
                FUSION_HOME=${2}
                shift 2
            ;;
            -h|--help)
            print_usage
                exit 1
            ;;
            -H|--hostname)
                if [[ -z "$2" || "${2:0:1}" == "-" ]]; then
                    print_usage "hostname is required when using the $1 option!"
                    exit 1
                fi
                SSH_HOSTNAME=${2}
                shift 2
            ;;
            -l|--fusion-license)
                if [[ -z "$2" || "${2:0:1}" == "-" ]]; then
                    print_usage "path to license.properties is required when using the $1 option!"
                    exit 1
                fi
                FUSION_LICENSE=${2}
                shift 2
            ;;
            -i|--identity)
                if [[ -z "$2" || "${2:0:1}" == "-" ]]; then
                    print_usage "ssh identity is required when using the $1 option!"
                    exit 1
                fi
                IDENTITY_FILE=${2}
                shift 2
            ;;
            -s|--searchhub_home)
                if [[ -z "$2" || "${2:0:1}" == "-" ]]; then
                    print_usage "path for searchhub home is required when using the $1 option!"
                    exit 1
                fi
                SEARCHHUB_HOME=${2}
                shift 2
            ;;
            -t|--twigkit-credentials)
                if [[ -z "$2" || "${2:0:1}" == "-" ]]; then
                    print_usage "path to settings.xml is required when using the $1 option!"
                    exit 1
                fi
                TWIGKIT_CREDENTIALS=${2}
                shift 2
            ;;
            -u|--username)
                if [[ -z "$2" || "${2:0:1}" == "-" ]]; then
                    print_usage "username is required when using the $1 option!"
                    exit 1
                fi
                USERNAME=${2}
                shift 2
            ;;
            w|--wipe-old-install)
                WIPE_OLD_INSTALL=1
                shift 2
            ;;
            -*)
                print_usage "The $1 option does not exist!"
                exit 1
            ;;
            *)
                if [ "$1" != "" ]; then
                    PASS_THRU_ARGS+=("$1")
                    shift
                else
                    break
                fi
            ;;
        esac
    done
fi

if [[ -z "$FUSION_HOME" ]]; then
    FUSION_HOME=/home/${USERNAME}/fusion
fi

if [[ -z "$SEARCHHUB_HOME" ]]; then
    SEARCHHUB_HOME=/home/${USERNAME}/src/lucidworks/searchhub
fi

echo ${TWIGKIT_CREDENTIALS}
echo ${FUSION_LICENSE}
echo $FUSION_HOME
echo $SEARCHHUB_HOME

#exports vars and runs UploadFiles.sh
. ${INSTALLER_HOME}/scripts/upload_files.sh
ssh -i ${IDENTITY_FILE} ${USERNAME}@${SSH_HOSTNAME} "export USERNAME=${USERNAME}; export FUSION_HOME=${FUSION_HOME}; export SEARCHHUB_HOME=${SEARCHHUB_HOME}; export DATA_SOURCES=${DATA_SOURCES}; export WIPE_OLD_INSTALL=${WIPE_OLD_INSTALL}; ./fusion_installer.sh"
