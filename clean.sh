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
set -x

source "$DEMO_HOME/myenv.sh"

echo "Exporting the App just in case to /tmp/ecommerce.zip"
curl "$FUSION_API/objects/export?app.ids=ecommerce&app.ids=customer360&blob.ids=ecom_keyword.csv&blob.ids=stop.rtf" > "/tmp/ecommerce.zip"

curl  -X DELETE "$FUSION_API/webapps/ecommerce"
curl  -X DELETE "$FUSION_API/webapps/customer360"
curl  -X DELETE "$FUSION_API/webapps/ruleseditor"
curl  -X DELETE "$FUSION_API/apps/ecommerce"
curl  -X DELETE "$FUSION_API/apps/customer360"
curl -X DELETE "$FUSION_API/apps/ecommerce/collections/ecommerce?purge=true&pipelines=true&solr=true"
curl -X DELETE "$FUSION_API/apps/customer360/collections/customer360?purge=true&pipelines=true&solr=true"
