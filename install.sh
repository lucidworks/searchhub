#!/usr/bin/env bash
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

cd "$DEMO_HOME"
OPTIND=1
no_build=0
no_crawl=0

while getopts "hbc" opt; do
    case "$opt" in
    h|\?)
        echo "do something else, no help here"
        exit 0
        ;;
    b)  no_build=1
        ;;
    c)  no_crawl=1
        ;;
    esac
done

shift $((OPTIND-1))

[ "$1" = "--" ] && shift

echo "No Build=$no_build, No Crawl=$no_crawl, Leftovers: $@"

# Install any custom Spark stuff
if [ "$no_build" -eq 0 ]; then
    cd "$DEMO_HOME/client"
    mvn clean package
fi

# TODO: download the data, check if it is there, unzip,
#cd "$DEMO_HOME/data"

cd "$DEMO_HOME/setup"


echo "Installing the Application"
echo ""
cd "$DEMO_HOME/setup/app"
zip -r tmp.zip objects.json blobs/* configsets/*
curl -H "Content-Type:multipart/form-data" -X POST -F 'importData=@tmp.zip' "$FUSION_API/objects/import?importPolicy=overwrite"
rm tmp.zip
cd "$DEMO_HOME/setup"

curl -H 'Content-type: application/json' -X POST -d "@searchhub_appstudio.json" "$FUSION_API/webapps"
curl -H 'Content-type: application/zip' -X PUT "$FUSION_API/webapps/searchhub/war" --data-binary "@../client/dist/searchhub.war"