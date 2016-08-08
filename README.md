# Lucidworks Search Hub
  
  Search Hub is an application built on top of [Lucidworks Fusion](http://www.lucidworks.com/products/fusion).  
  It is designed to be a showcase of Fusion's search, machine learning and analytical capability
   as well as act as a community service for a large number of Apache Software Foundation projects.  It is the basis of several talks
    by Lucidworks employees (e.g. http://www.slideshare.net/lucidworks/data-science-with-solr-and-spark).  A production version of this software hosted by [Lucidworks](http://www.lucidworks.com) is available
    at http://searchhub.lucidworks.com. 
   
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

- [Node.js](http://nodejs.org) 5.x: Use the installer for your OS, e.g. ```brew install homebrew/versions/node5```
- [Git](http://git-scm.com/downloads): Use the installer for your OS.

- Depending on how Node is configured on your machine, you may need to run `sudo npm install -g gulp bower` instead, if you get an error with the first command.
- Python 2.7 and python-dev
- Fusion 2.4.1 or later.  Download at http://www.lucidworks.com/products/fusion and install in a directory reachable from this project.


## Get Started

In ~/.gradle/gradle.properties, add/set:

```
searchhubFusionHome=/PATH/TO/FUSION/INSTALL
```

The searchhubFusionHome variable is used by the build to know where to deploy custom plugins that the Search Hub project needs (namely, a Mail Parsing Stage)

If you haven't already, clone this repository and change into the directory of the clone.

  ```bash
  git clone https://github.com/LucidWorks/searchhub
  cd searchhub
  ```  

Run the Installer to install NPM, Bower and Python dependencies

```bash
./gradlew install
```

(Re)Start your Fusion instance (see Requirements above, this needs to be Fusion 2.4.x)
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
../venv/bin/python bootstrap.py
```

The bootstrap.py step creates a number of objects in Fusion, including collections, pipelines, schedules and data sources.  By default, the start up 
script does not start the crawler, nor does it enable the schedules.  If you wish to start them, visit the Fusion Admin UI or do one of the following:
 
 To run the data sources once, upon creation (note: this can be quite expensive, as it will start all datasources):
 
 ```bash
 cd python
 ../venv/bin/python bootstrap.py --start_datasources
 ```
 
 To enable the schedules, edit your config.py and set ```ENABLE_SCHEDULES=True``` and then rerun ```python bootstrap.py```


## Running Search Hub

### Local, Non-Production Mode using Werkzeug

Run Flask (from the python directory):

```bash
cd python
../venv/bin/python run.py
```


Browse to http://localhost:5000

If you make changes to the UI, you will either need to rebuild the UI part (npm build) or run:

```bash
npm watch
```

### Production

#### Docker

The easiest way to spin up the Search Hub Client and Python app is by using [Docker](https://www.docker.com/) and the Dockerfile in the Python directory.

This container is built on httpd and [mod_wsgi](https://github.com/GrahamDumpleton/mod_wsgi-docker/)

To build a container, do the following steps:

1. Edit your FUSION_CONFIG.js to point to the IP of your container.  You can do also do this afterwards too, by attaching to the running container and editing it.
1. Build the SearchHub UI (see above) so that the Client assets are properly installed in the Python ```server``` directory
1. ```cd python```
1. Create a ```config-docker.py``` file that contains the configuration required to connect to your Fusion instance.  Note, this Docker container we are running now does not run Fusion. 
1. ```docker build -t searchhub .```  -- This builds the Docker container
1. ```docker run -it --rm -p 8000:80 --name searchhub searchhub``` -- This runs the container and maps to port 8000.  See Docker help for otherways to run Docker containers
1. Point your browser at http://host:8000/  where host is the IP for your Docker container.

Some other helpful commands:

1. ```docker rmi -f searchhub``` -- delete a previously built version of the container


#### WSGI Compliant Server

See docker.sh in the Home directory for how to build and run mod_wsgi_express in a Docker container.


# The Client Application

The Client Application is an extension of [Lucidworks View](http://www.lucidworks.com/products/view) and thus relies on similar build and layout
mechanisms and structures.  It is an Angular app and leverages FoundationJS.  We have extended it to use the [Snowplow Javascript Tracker](https://github.com/snowplow/snowplow/wiki/javascript-tracker)
for capturing user interactions.  All of these interactions are fed through the Flask middle tier and then on to Fusion for use by our clickstream and machine learning
capabilities.

### Configuration

In order to configure the client application you can change the settings in the FUSION_CONFIG.js.  See the [View](http://www.lucidworks.com/products/view) docs
for more details or read the comments in the config file itself.


# Extending

Pull Requests are welcome for new projects, new configurations and other new extensions.

## Project Layout

The Search Hub project consists of 3 main development areas, plus build infrastructure:
 
### Client

Written in Javascript, using AngularJS and Foundation, the Client is located in the ```client``` directory.  It's build is a bit different than most JS builds
in that it copies Lucidworks View from the node_modules download area into a temporary ```build``` directory and then copies in the Search Hub client code into
the same directory and then it gets built and moved to the Flask application serving area (```python/server```).  We are working on ways to improve how View is
extended and so this approach, while viable for now, may change.  Our goal is to have most of the Client UI be driven by View itself with very little
extension in Search Hub.

### Python

The ```python``` directory contains all of the Flask application and acts as the middle tier in the application between the client and Fusion.  Most of the
work in the application is initiated by either the ```bootstrap.py``` file or the ```run.py``` file.  The former is responsible for using the configurations
in ```python/fusion_config``` and ```python/project_config``` to, as the name implies, bootstrap Fusion with datasources, pipeline definitions, schedules and
whatever else is needed to make sure Fusion has the appropriate data necessary to function.  The latter file (run.py) is a Flask app that takes
care of the serving of the Flask application.  It primarily consists of routing information as well as a thin proxy to Fusion.

Most of the Python work is defined by the ```python/server``` directory.  This directory and it's children define how Flask talks to 
 Fusion and also defines some template helpers for creating various datasources in Fusion.  A good starting place for learning more
 is the ```fusion.py``` file in ```python/server/backends```
 
### Fusion Plugins

The ```searchhub-fusion-plugins``` directory contains Java and Scala code for extending and/or utilizing Fusion's backend capabilities.
On the Java side, the two main functions are:  

1. A Mail Parsing Stage that is responsible for extracting pertinent information out of Mail messages (e.g. thread ids, to/from)
1. A Mail downloader.  Since we don't want to tax Apache Software Foundation resources directly when crawling (they have a banning mechanism), we have setup an httpd mod_mbox mirror.  
The mail downloader is responsible for retrieving the daily mbox messages.  If you wish to have a local mirror for your own purposes, you can use this class to get your own mbox files.

On the Scala side, there are a number of Spark Scala utilities that show how to leverage Lucene analysis in Spark, run common SparkML tasks like LDA and k-Means plus some 
code for correlating email messages based on message ids.  See Grant Ingersoll's talk at the Dallas Data Science [meetup](http://www.slideshare.net/lucidworks/data-science-with-solr-and-spark) for details.
To learn more on the Scala side, start with the ```SparkShellHelpers.scala``` file.

### The Build

The build is primarily driven by Gradle and Gulp.  Gradle defines tasks, per the getting started above, for all necessary tasks needed to run Search Hub.  
However, on the client side of things, it is simply invoking npm or Gulp to do the Javascript build.  To learn more about the build, see ```build.gradle```.



## Adding your own Project to Crawl

To add another project, you need to do a few things:

1. In $FUSION_HOME/python/project_config, create/copy/edit a project configuration file.  See accumulo.json as an example.
1. In $FUSION_HOME/searchhub-fusion-plugins/src/main/resources, edit the mailing_lists.csv to add your project.
1. If you are adding more mailing lists, you will need to either crawl the ASF's mail archives site (please be polite when doing so) or setup an 
   httpd mod_mbox instance like we have at http://asfmail.lucidworks.io.  If you submit a pull request against this project with your mailing_lists.csv changes, we will consider adding it to our hosted version.
