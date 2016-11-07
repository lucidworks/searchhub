#!flask/bin/python
from __future__ import print_function

import json
# Bootstrap the database
from server import app, cmd_args, create_all


# TODO some migration logic

# Bootstrap the Fusion configs (collection, datasources, pipelines, etc)
import json
from os import listdir
from os.path import isfile, join

from server import backend
from server.backends.fusion import new_admin_session

# Use the Solr Config API to bootstrap search_components and request handlers
def setup_request_handlers(backend, collection_id):
  #create search components before req handlers
  files = [f for f in listdir("./fusion_config/" + collection_id) if isfile(join("./fusion_config/" + collection_id, f)) and f.endswith("_search_component.json")]
  for file in files:
    print ("Creating Search Components for %s" % file)
    backend.add_search_component(collection_id, json.load(open(join("./fusion_config/" + collection_id, file))))

  files = [f for f in listdir("./fusion_config/" + collection_id) if isfile(join("./fusion_config/" + collection_id, f)) and f.endswith("_request_handler.json")]
  for file in files:
    print ("Creating Request Handler for %s" % file)
    backend.add_request_handler(collection_id, json.load(open(join("./fusion_config/" + collection_id, file))))

# Setup any necessary solr field types, like those used for suggestions
def setup_field_types(backend, collection_id):
  field_types = [f for f in listdir("./fusion_config/" + collection_id) if isfile(join("./fusion_config/" + collection_id, f)) and f.endswith("_field_type.json")]
  for file in field_types:
    print ("Creating Field Type for %s" % file)
    backend.add_field_type(collection_id, json.load(open(join("./fusion_config/" + collection_id, file))))

def setup_commit_times(backend, collection_id, time_in_ms=10*60*1000):
  data = {
    "updateHandler.autoCommit.maxTime": time_in_ms, #10 minutes by default
  }

  backend.set_property(collection_id, data)

# Setup an official schema for things we know we are going to have in the data
def setup_find_fields(backend, collection_id):
  backend.add_field(collection_id, "publishedOnDate", type="tdate", required=True)
  backend.add_field(collection_id, "suggest", type="suggesterFT", multivalued=True)
  backend.add_field(collection_id, "content", type="text_en")
  backend.add_field(collection_id, "project", type="string", copyDests=["suggest"])
  backend.add_field(collection_id, "project_label", type="string", copyDests=["suggest"])
  backend.add_field(collection_id, "datasource_label", type="string")
  backend.add_field(collection_id, "body", type="text_en")
  backend.add_field(collection_id, "title", type="text_en", copyDests=["suggest"])
  backend.add_field(collection_id, "keywords", type="text_en", copyDests=["suggest"])
  backend.add_field(collection_id, "comments", type="text_en")
  backend.add_field(collection_id, "mimeType", type="string")
  backend.add_field(collection_id, "author_facet", type="string")
  backend.add_field(collection_id, "author", type="text_en", copyDests=["author_facet"])
  backend.add_field(collection_id, "og_description", type="text_en")
  backend.add_field(collection_id, "description", type="text_en")
  backend.add_field(collection_id, "subject", type="text_en", copyDests=["suggest"])
  backend.add_field(collection_id, "filename_exact", type="string")
  backend.add_field(collection_id, "filename", type="text_en", copyDests=["filename_exact"])
  backend.add_field(collection_id, "length", type="int")
  backend.add_field(collection_id, "isBot", type="boolean")
  backend.add_field(collection_id, "productVersion", type="float") # If we are dealing w/ an LW product, can we determine it's version?
  backend.add_field(collection_id, "productName", type="string")
  backend.add_field(collection_id, "threadId", type="string")
  #backend.add_field(collection_id, "isDocumentation", type="boolean")

# ((fusion)/(\d+.\d+))|((\w+|LucidWorksSearch-Docs)-v(\d+\.\d+))

def setup_experiments(backend, collection_id):    
  job_files = [f for f in listdir("./fusion_config/" + collection_id) if isfile(join("./fusion_config/" + collection_id, f)) and f.endswith("_experiment.json")]    
  for file in job_files:    
    print ("Creating Experiment for %s" % file)   
    backend.create_experiment(json.load(open(join("./fusion_config/" + collection_id, file))))

# Setup schema for user collection
def setup_user_fields(backend, collection_id):
  backend.add_field(collection_id, "username", type="string", required=True)
  backend.add_field(collection_id, "email", type="string", required=True)
  backend.add_field(collection_id, "password", type="string", required=True)
  backend.add_field(collection_id, "first_name", type="string", required=True)
  backend.add_field(collection_id, "last_name", type="string", required=True)

# Loop over the Fusion config and add any pipelines defined there.
def setup_pipelines(backend, collection_id):
  pipe_files = [f for f in listdir("./fusion_config/" + collection_id) if isfile(join("./fusion_config/" + collection_id, f)) and f.endswith("_pipeline.json")]
  for file in pipe_files:
    print ("Creating Pipeline for %s" % file)
    if file.find("query") != -1:
      backend.create_pipeline(json.load(open(join("./fusion_config/" + collection_id, file))), pipe_type="query-pipelines")
    else:
      backend.create_pipeline(json.load(open(join("./fusion_config/" + collection_id, file))))

def setup_batch_jobs(backend, collection_id):
  job_files = [f for f in listdir("./fusion_config/" + collection_id) if isfile(join("./fusion_config/" + collection_id, f)) and f.endswith("_job.json")]
  for file in job_files:
    print ("Creating Batch Job for %s" % file)
    backend.create_batch_job(json.load(open(join("./fusion_config/" + collection_id, file))))

# Create the taxonomy, which can be used to alter requests based on hierarchy
def setup_taxonomy(backend, collection_id):
  status = backend.delete_taxonomy(collection_id)
  taxonomy = json.load(open('fusion_config/' + collection_id + '/taxonomy.json'))
  status = backend.create_taxonomy(collection_id, taxonomy)

# Schedule all non-datasource by looking in fusion_config/  + collection_idfor schedule declarations
def setup_schedules(backend, collection_id):
  files = [f for f in listdir("./fusion_config/" + collection_id) if isfile(join("./fusion_config/" + collection_id, f)) and f.endswith("_schedule.json")]
  for file in files:
    print("Creating Schedule for %s" % file)
    backend.create_or_update_schedule(json.load(open(join("./fusion_config/" + collection_id, file))))

# bootstrap.py --start_schedules
def start_schedules(backend):
  backend.activate_schedules()

# bootstrap.py --stop_schedules
def stop_schedules(backend):
  backend.stop_schedules()

def stop_datasources(backend):
  backend.stop_datasources()

# Map the project_config/  + collection_id directory into Fusion datasources and schedules.
def setup_projects(backend, collection_id):
  project_files = [f for f in listdir("./project_config/" + collection_id ) if isfile(join("./project_config/" + collection_id , f)) and f.endswith(".json")]
  if cmd_args.start_datasources:
    print("Each data source created will also be started")
  else:
    print("")
    print("Skipping starting the datasources.  Pass in --start_datasources if you wish to start them when bootstrapping")

  for file in project_files: #TODO: what's the python way here?
    print ("Creating Project for %s" % file)
    project = json.load(open(join("./project_config/" + collection_id , file)))
    print("Bootstraping configs for %s..." % project["name"])
    #create the data sources
    datasources = []
    (twitter_config, jira_config, mailbox_configs, wiki_configs, website_configs, github_configs, stack_configs) = backend.create_or_update_datasources(project)
    datasources.append(twitter_config)
    datasources.append(jira_config)
    datasources.extend(mailbox_configs)
    datasources.extend(wiki_configs)
    datasources.extend(website_configs)
    datasources.extend(github_configs)
    datasources.extend(stack_configs)

    for datasource in datasources:
      if datasource:
        # start the data sources
        if cmd_args.start_datasources:
          print ("Stop existing datasource %s if it exists" % datasource["id"])
          backend.stop_datasource(datasource, abort=True)
          print("Starting datasource %s" % datasource["id"])
          #TODO
          backend.start_datasource(datasource["id"])

backend.toggle_system_metrics(False)
backend.set_log_level("WARN")

backend.update_logging_scheduler()

lucidfind_collection_id = app.config.get("FUSION_COLLECTION", "lucidfind")
lucidfind_batch_recs_collection_id = app.config.get("FUSION_BATCH_RECS_COLLECTION", "lucidfind_thread_recs")
user_collection_id = app.config.get("USER_COLLECTION", "users")

collection1_id = app.config.get("FUSION_COLLECTION1")
collection2_id = app.config.get("FUSION_COLLECTION2")
collection3_id = app.config.get("FUSION_COLLECTION3")

# Create our main application user
username = app.config.get("FUSION_APP_USER", "lucidfind")
if cmd_args.create_collections or create_all:
  update_permissions = {
    "permissions": [
      {
        "methods": [
          "GET"
        ],
        "path": "/query-pipelines/shub-typeahead/collections/{0}/suggest".format(lucidfind_collection_id)
      },
      {
        "methods": [
          "GET"
        ],
        "path": "/query-pipelines/lucidfind-default/collections/{0}/select".format(lucidfind_collection_id)
      },
      {
        "methods": [
          "GET"
        ],
        "path": "/query-pipelines/lucidfind-recommendations/collections/{0}/select".format(lucidfind_collection_id)
      },
      {
        "methods": [
          "GET"
        ],
        "path": "/query-pipelines/cf-similar-items-rec/collections/{0}/select".format(lucidfind_collection_id)
      },
      {
        "methods": [
          "GET"
        ],
        "path": "/query-pipelines/cf-similar-items-batch-rec/collections/{0}/select".format(lucidfind_batch_recs_collection_id)
      },
      {
        "methods": [
          "GET"
        ],
        "path": "/collections/{0}/query-profiles/lucidfind-default/select".format(lucidfind_collection_id)
      },
      {
        "methods": [
          "GET"
        ],
        "path": "/collections/{0}/query-profiles/default/select".format(lucidfind_collection_id)
      },
      {
        "methods": [
          "GET"
        ],
        "path": "/signals/{0}/i".format(lucidfind_collection_id)
      },   
      {   
        "methods": [    
          "GET"   
        ],# Make this more flexible, as this is hardcoded now   
        "path": "/experiments/jobs/download_v_learn_more/variant"   
      },    
      {   
        "methods": [    
          "PUT"   
        ],    
        "path": "/experiments/jobs/download_v_learn_more/variant/*"
      }
    ]
  }

  backend.update_role("search", update_permissions)
status = backend.create_user(username, app.config.get("FUSION_APP_PASSWORD"))
if status == False:
  exit(1)

# Create the collection, setup fields and other solr pieces
if cmd_args.create_collections or create_all:
  session = new_admin_session()
  # Create the "lucidfind" collection
  solr_params = {"replicationFactor":2,"numShards":1}
  status = backend.create_collection(lucidfind_collection_id, enable_signals=True, solr_params=solr_params, default_commit_within=60*10*1000)
  status1 = backend.create_collection(collection1_id, enable_signals=True, solr_params=solr_params, default_commit_within=60*10*1000)
  status2 = backend.create_collection(collection2_id, enable_signals=True, solr_params=solr_params, default_commit_within=60*10*1000)
  status3 = backend.create_collection(collection3_id, enable_signals=True, solr_params=solr_params, default_commit_within=60*10*1000)
  if status == False or status1 == False or  status2 == False or status3 == False:
    exit(1)
  # Due to a bug in Solr around suggesters, let's try to remove the suggester first
  #backend.remove_request_handler(lucidfind_collection_id, "/suggest")
  #backend.remove_search_component(lucidfind_collection_id, "suggest")
  setup_field_types(backend, lucidfind_collection_id)
  setup_find_fields(backend, lucidfind_collection_id)
  setup_request_handlers(backend, lucidfind_collection_id)
  setup_commit_times(backend, lucidfind_collection_id)
  setup_commit_times(backend, "logs", 5*60*1000)
  setup_commit_times(backend, "lucidfind_logs", 5*60*1000)
  
  setup_field_types(backend, collection1_id)
  setup_find_fields(backend, collection1_id)
  setup_request_handlers(backend, collection1_id)
  setup_commit_times(backend, collection1_id)
  
  setup_field_types(backend, collection2_id)
  setup_find_fields(backend, collection2_id)
  setup_request_handlers(backend, collection2_id)
  setup_commit_times(backend, collection2_id)

  setup_field_types(backend, collection3_id)
  setup_find_fields(backend, collection3_id)
  setup_request_handlers(backend, collection3_id)
  setup_commit_times(backend, collection3_id)

  status = backend.create_collection("lucidfind_thread_recs")
  if status == False:
    exit(1)

  # Create the "users" collection for registration
  status = backend.create_collection(user_collection_id, enable_signals=False, enable_search_logs=False, enable_dynamic_schema=False)
  if status == False:
    exit(1)
  setup_user_fields(backend, user_collection_id)

#create the pipelines
if cmd_args.create_pipelines or create_all:
  setup_pipelines(backend, lucidfind_collection_id)
  backend.create_query_profile(lucidfind_collection_id, "lucidfind-default", "lucidfind-default")


if cmd_args.create_taxonomy or create_all:
  setup_taxonomy(backend, lucidfind_collection_id)

# Configure each Project.
if cmd_args.create_projects or create_all:
  print("Creating Projects")
  setup_projects(backend, lucidfind_collection_id)

if cmd_args.create_batch_jobs or create_all:
  setup_batch_jobs(backend, lucidfind_collection_id)

#create the schedules
if cmd_args.create_schedules or create_all:
  setup_schedules(backend, lucidfind_collection_id)

if cmd_args.create_experiments or create_all:
  setup_experiments(backend, lucidfind_collection_id)

if cmd_args.start_schedules:
  start_schedules(backend, lucidfind_collection_id)

if cmd_args.stop_schedules:
  stop_schedules(backend,lucidfind_collection_id)

if cmd_args.stop_datasources:
  stop_datasources(backend, lucidfind_collection_id)