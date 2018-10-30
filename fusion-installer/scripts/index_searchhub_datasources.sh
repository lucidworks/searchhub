#!/bin/bash

#USERNUM=2
#
#FINISHED_INDEXING=0
#INDEXER_STATUS="FINISHED"
DATA_SOURCES=0

if [ $# == 0 ]; then
    echo "missing options, please use -h or --help to see all available options"
    exit 1
fi

function print_usage() {
    ERROR_MSG="$1"

    if [ "$ERROR_MSG" != "" ]; then
        echo -e "\nERROR: $ERROR_MSG\n"
    fi
}


#options
if [ $# -gt 0 ]; then
    while true; do
        case $1 in
            -d  | --datasource-list)
                if [[ -z "$2" || "${2:0:1}" == "-" ]]; then
                    print_usage "a list of datasources is required when using the $1 option!"
                    exit 1
                fi
                DATA_SOURCES=${2}
                shift 2
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

if [ "${missing_argument}" != "" ]; then
    echo "${missing_argument} requires an argument please use -h or --help"
    exit 1
fi

IFS=',' read -r -a array <<< "${DATA_SOURCES}"

for DATA_SOURCE in "${array[@]}"
do
    echo "curl -u admin:password123 -X  POST http://localhost:8764/api/apollo/connectors/jobs/${DATA_SOURCE}"
    curl -u admin:password123 -X  POST http://localhost:8764/api/apollo/connectors/jobs/${DATA_SOURCE}
done

