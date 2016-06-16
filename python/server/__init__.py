# Create the application itself
import sys
import argparse
from flask import Flask
#from flask.ext.basicauth import BasicAuth


parser = argparse.ArgumentParser(description='Setup Search Hub')
parser.add_argument('--start_datasources', action='store_true',
                            help='start the datasources when bootstrapping')
parser.add_argument('--stop_datasources', action='store_true',
                            help='stop all datasources')
parser.add_argument('--create_collections', action='store_true',
                            help='create the collections')
parser.add_argument('--create_projects', action='store_true',
                            help='create the projects')
parser.add_argument('--create_pipelines', action='store_true',
                            help='create/update the pipelines')
parser.add_argument('--create_taxonomy', action='store_true',
                            help='create/update the taxonomy')
parser.add_argument('--create_schedules', action='store_true',
                            help='create/update the schedules')
parser.add_argument('--create_all', action='store_true',
                            help='create all items, as if setting all flags.  You can also just not pass in any arguments')
parser.add_argument('--config', action='store',
                            help='The config file to use, default is "config.py"')
parser.add_argument('--start_schedules', action='store_true',
                            help='Activate all schedules.  Only SearchHub schedules will be activated')
parser.add_argument('--stop_schedules', action='store_true',
                            help='Stop all active schedules.  Only SearchHub schedules will be de-activated')
cmd_args = parser.parse_args()

create_all = False
# If we have no cmd line args, then create all
if len(sys.argv) == 1 or cmd_args.create_all:
  create_all = True

config = "config"
if cmd_args.config:
  config = cmd_args.config

#from proxy
app = Flask(__name__, static_folder="assets", template_folder="flask_templates")
print "Using config: " + config
app.config.from_object(config)
app.config.from_envvar("CONFIG_PY", silent=True)
#app.basic_auth = BasicAuth(app)

# Import and initialize the backend
from server.backends import get_backend
backend = get_backend()

# Import our views
from server.views import *

import proxy

