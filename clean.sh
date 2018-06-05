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

echo "Exporting the App just in case to /tmp/searchhub.zip"
curl "$FUSION_API/objects/export?app.ids=searchhub&blob.ids=lucidworks.jira-4.1.0-SNAPSHOT.zip&blob.ids=lucidworks.github-4.1.0-SNAPSHOT.zip&blob.ids=lucidworks.twitter-stream-4.1.0-SNAPSHOT.zip" > "/tmp/searchhub.zip"