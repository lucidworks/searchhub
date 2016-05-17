# Lucidworks Search Hub
  
  Search Hub is an application built on top of [Lucidworks Fusion](http://www.lucidworks.com/products/fusion).  
  It is designed to be a showcase of Fusion's search, machine learning and analytical capability
   as well as act as a community service for a large number of Apache Software Foundation projects.  It is the basis of several talks
    by Lucidworks employees (e.g. http://www.slideshare.net/lucidworks/data-science-with-solr-and-spark).  A production version of this software hosted by [Lucidworks](http://www.lucidworks.com) will
   be available soon. 
   
   Search Hub contains all you need to download and run your own community search site. It comes with prebuilt definitions to crawl a large number of ASF projects, including
   their mailing lists, websites, wikis, JIRAs and Github repositories.  These prebuilt definitions may also serve as templates for adding additional projects.  The project
   also comes in with a built-in client (based off of [Lucidworks View](http://www.lucidworks.com/products/view)
   
   This application uses [Snowplow](https://github.com/snowplow/snowplow) for tracking on the website.  In particular, it tracks:
   1. Page visits
   1. Time on page (via page pings)
   1. Location
   1. Clicks on documents and facets
   1. Searches
   
   Search Hub is open source under the Apache License, although
   do note Lucidworks Fusion itself is not open source.

## Requirements

  You'll need the following software installed to get started.

- [Node.js](http://nodejs.org): Use the installer for your OS.
- [Git](http://git-scm.com/downloads): Use the installer for your OS.

- Depending on how Node is configured on your machine, you may need to run `sudo npm install -g gulp bower` instead, if you get an error with the first command.
- Python 2.7 and python-dev
- Fusion 2.3 or later.  Download at http://www.lucidworks.com/products/fusion and install in a directory reachable from this project.


## Get Started

In ~/.gradle/gradle.properties, add/set:

```
searchhubFusionHome=/PATH/TO/FUSION/INSTALL
```

Clone this repository and change into the directory

  ```bash
  git clone https://github.com/LucidWorks/searchhub
  cd searchhub
  ```  

Run the Installer to install NPM, Bower and Python dependencies

```bash
./gradlew install
```

(Re)Start your Fusion instance (see Requirements above, this needs to be Fusion from the "searchhub" branch)
  This is important since ```deployLibs``` (task called by the install task) installed the MBoxParsingStage into Fusion.


Build the UI: This will copy the client files into python/server

```bash
./gradlew buildUI
```

  If you prefer using Gulp, you can also run ```gulp build```

Setup Python Flask:

```bash
source venv/bin/activate
cd python
cp sample-config.py config.py
#fill in config.py as appropriate. You will need Twitter keys to make Twitter work.
python bootstrap.py
```

The bootstrap.py step creates a number of objects in Fusion, including collections, pipelines, schedules and data sources.  By default, the start up 
script does not start the crawler, nor does it enable the schedules.  If you wish to start them, visit the Fusion Admin UI or do one of the following:
 
 To run the data sources once, upon creation (note: this can be quite expensive, as it will start all datasources):
 
 ```bash
 python bootstrap.py --start_datasources
 ```
 
 To enable the schedules, edit your config.py and set ```ENABLE_SCHEDULES=True``` and then rerun ```python bootstrap.py```


## Running Search Hub

Run Flask (from the python directory):

```bash
python run.py
```


Browse to http://localhost:5000

If you make changes to the UI, you will either need to rebuild the UI part (npm build) or run:

```bash
npm watch
```


# The Client Application

The Client Application is an extension of [Lucidworks View](http://www.lucidworks.com/products/view) and thus relies on similar build and layout
mechanisms and structures.  It is an Angular app and leverages FoundationJS.  We have extended it to use the [Snowplow Javascript Tracker](https://github.com/snowplow/snowplow/wiki/javascript-tracker)
for capturing user interactions.  All of these interactions are fed through the Flask middle tier and then on to Fusion for use by our clickstream and machine learning
capabilities.

### Configuration

In order to configure the client application you can change the settings in the FUSION_CONFIG.js.  See the [View](http://www.lucidworks.com/products/view) docs
for more details or read the comments in the config file itself.


# Extending

## Adding your own Project

To add another project, you need to do a few things:

1. In $FUSION_HOME/python/project_config, create/copy/edit a project configuration file.  See accumulo.json as an example.
1. In $FUSION_HOME/searchhub-fusion-plugins/src/main/resources, edit the mailing_lists.csv to add your project.
1. If you are adding more mailing lists, you will need to either crawl the ASF's mail archives site (please be polite when doing so) or setup an 
   httpd mod_mbox instance like we have at http://asfmail.lucidworks.io.  If you submit a pull request against this project with your mailing_lists.csv changes, we will consider adding it to our hosted version.
