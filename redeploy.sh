#!/usr/bin/env bash

while [ -h "$SETUP_SCRIPT" ] ; do
  ls=`ls -ld "$SETUP_SCRIPT"`
  # Drop everything prior to ->
  link=`expr "$ls" : '.*-> \(.*\)$'`
  if expr "$link" : '/.*' > /dev/null; then
    SETUP_SCRIPT="$link"
  else
    SETUP_SCRIPT=`dirname "$SETUP_SCRIPT"`/"$link"
  fi
done

DEMO_HOME=`dirname "$SETUP_SCRIPT"`
DEMO_HOME=`cd "$DEMO_HOME"; pwd`

source "$DEMO_HOME/myenv.sh"


curl  -X DELETE "$FUSION_API/webapps/searchhub"
cd "$DEMO_HOME/client"
mvn -o package
cd "$DEMO_HOME/setup"

curl -H 'Content-type: application/json' -X POST -d "@searchhub_appstudio.json" "$FUSION_API/webapps"
echo "deploying war"
curl -H 'Content-type: application/zip' -X PUT "$FUSION_API/webapps/searchhub/war" --data-binary "@../client/dist/searchhub.war"

#cd "$FUSION_HOME/"
#bin/webapps restart
