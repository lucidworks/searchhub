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

- Fusion 4.1.0 (or 4.1.0-SNAPSHOT if this is before it's released)
- The Github sources require a Github API key: https://github.com/blog/1509-personal-api-tokens
- If you want to crawl Twitter, you will need Twitter keys: https://dev.twitter.com/oauth/overview

## Get Started

0. Copy `myenv.sh.tmpl` to `myenv.sh` and fill in with appropriate values.  Usually this means setting the FUSION_HOME variable.
1. `source myenv.sh`
1. Copy `password_file.json.tmp` to `password_file.json` and fill in appropriately.  As of this time, this file must be in plaintext, so please treat it appropriately.
1. `./gradlew deployLibs` (this will deploy the mail parsing code to Fusion)
1. Restart the Fusion API and Connector services:
      1. In $FUSION_HOME, `bin/api restart` and `bin/connectors restart`
1. `./install.sh`                                                          


## Adding your own Project to Crawl

To add another project, you need to do a few things:

1. In $FUSION_HOME/python/project_config, create/copy/edit a project configuration file.  See accumulo.json as an example.
1. In $FUSION_HOME/searchhub-fusion-plugins/src/main/resources, edit the mailing_lists.csv to add your project.
1. If you are adding more mailing lists, you will need to either crawl the ASF's mail archives site (please be polite when doing so) or setup an 
   httpd mod_mbox instance like we have at http://asfmail.lucidworks.io.  If you submit a pull request against this project with your mailing_lists.csv changes, we will consider adding it to our hosted version.
