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

if [ ! -f "$DEMO_HOME/myenv.sh" ]; then
    # no myenv.sh but maybe they gave us the path to Fusion as an arg?
    if [ "$1" != "" ]; then
	if [ -d "$1" ]; then
	    cp $DEMO_HOME/myenv.sh.tmpl $DEMO_HOME/myenv.sh
	    SED_PATTERN="s|export FUSION_HOME=|export FUSION_HOME=$1|g"
	    sed -i.bak "$SED_PATTERN" $DEMO_HOME/myenv.sh
	    rm myenv.sh.bak
	    chmod +x $DEMO_HOME/myenv.sh
	    echo -e "\nCreated myenv.sh from arg $1\n"
	else
	    echo -e "\nERROR: $1 is not a valid Fusion home directory! Please pass the path to your Fusion\ninstallation or create a myenv.sh script with the correct settings for your Fusion installation.\n"
	    exit 1
	fi
    else
	echo -e "\nERROR: myenv.sh script not found! Please cp myenv.sh.tmp to myenv.sh and update it to reflect your Fusion settings.\nOr, if using all defaults, then simply pass the path to your Fusion installation to this script and a myenv.sh script will be created for you.\n"
	exit 1
    fi
fi

source "$DEMO_HOME/myenv.sh"

echo ""
echo "Exporting SearchHub App to setup/app/searchhub.zip"
# !!!!!!!!!!!!!!!!!!!
# If you change this line, be sure to change clean.sh as well.
# TODO: change this to take in a location, optionally, so we can use this script from clean.sh
# &app.ids=customer360&blob.ids=ecom_keyword.csv&blob.ids=stop.rtf
curl "$FUSION_API/objects/export?app.ids=searchhub&blob.ids=lucidworks.jira-4.1.0-SNAPSHOT.zip&blob.ids=lucidworks.github-4.1.0-SNAPSHOT.zip&blob.ids=lucidworks.twitter-stream-4.1.0-SNAPSHOT.zip" > "$DEMO_HOME/setup/app/searchhub.zip"
cd "$DEMO_HOME/setup/app"
unzip -q -o searchhub.zip
