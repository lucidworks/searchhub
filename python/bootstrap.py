#!flask/bin/python
from __future__ import print_function

import json
import requests
# Bootstrap the database
from server import app, cmd_args, create_all

# TODO some migration logic and code clean up 

# Bootstrap the Fusion configs (collection, datasources, pipelines, etc)
import json
from os import listdir
from os.path import isfile, join
from server import backend


# ------------------------------------------------------------------------------------------------ # 
# FUNCTION SETUP 

# Use the Solr Config API to bootstrap search_components and request handlers
def setup_request_handlers(backend, collection_id):
  files = [f for f in listdir("./fusion_config") if isfile(join("./fusion_config", f)) and f.endswith("_search_component.json")]
  for file in files:
    print ("Creating Search Components for %s" % file)
    backend.add_search_component(collection_id, json.load(open(join("./fusion_config", file))))

  files = [f for f in listdir("./fusion_config") if isfile(join("./fusion_config", f)) and f.endswith("_request_handler.json")]
  for file in files:
    print ("Creating Request Handler for %s" % file)
    backend.add_request_handler(collection_id, json.load(open(join("./fusion_config", file))))

# Setup any necessary solr field types, like those used for suggestions
def setup_field_types(backend, collection_id):
  field_types = [f for f in listdir("./fusion_config") if isfile(join("./fusion_config", f)) and f.endswith("_field_type.json")]
  for file in field_types:
    print ("Creating Field Type for %s" % file)
    backend.add_field_type(collection_id, json.load(open(join("./fusion_config", file))))

# Set up the commit times 
def setup_commit_times(backend, collection_id, time_in_ms=10*60*1000):
  data = {
    "updateHandler.autoCommit.maxTime": time_in_ms,  # 10 minutes by default
  }

  backend.set_property(collection_id, data)


# Setup an official schema for things we know we are going to have in the data
def setup_find_fields(backend, collection_id):
  backend.add_field(collection_id, "publishedOnDate", type="tdate", required=True)
  backend.add_field(collection_id, "suggest", type="suggesterFT", multivalued=True)
  backend.add_field(collection_id, "all_suggest", type="suggesterFT", multivalued=True)
  backend.add_field(collection_id, "content", type="text_en")
  backend.add_field(collection_id, "project", type="string", copyDests=["suggest"])
  backend.add_field(collection_id, "project_label", type="string", copyDests=["suggest"])
  backend.add_field(collection_id, "datasource_label", type="string")
  backend.add_field(collection_id, "body", type="text_en")
  backend.add_field(collection_id, "title", type="text_en", copyDests=["suggest"])
  backend.add_field(collection_id, "keywords", type="text_en", copyDests=["suggest"])
  backend.add_field(collection_id, "comments", type="text_en")
  backend.add_field(collection_id, "mimeType", type="string")
  backend.add_field(collection_id, "author_facet", type="string", multivalued=True)
  backend.add_field(collection_id, "author", type="text_en", copyDests=["author_facet"])
  backend.add_field(collection_id, "og_description", type="text_en")
  backend.add_field(collection_id, "description", type="text_en")
  backend.add_field(collection_id, "subject", type="text_en", copyDests=["suggest"])
  backend.add_field(collection_id, "filename_exact", type="string")
  backend.add_field(collection_id, "filename", type="text_en", copyDests=["filename_exact"])
  backend.add_field(collection_id, "length", type="int")
  backend.add_field(collection_id, "isBot", type="boolean")
  backend.add_field(collection_id, "productVersion", type="float") # TODO: If we are dealing w/ an LW product, can we determine it's version?
  backend.add_field(collection_id, "productName", type="string")
  backend.add_field(collection_id, "threadId", type="string")
  #backend.add_field(collection_id, "isDocumentation", type="boolean")

# ((fusion)/(\d+.\d+))|((\w+|LucidWorksSearch-Docs)-v(\d+\.\d+))

# Setup experiments we have specified 
def setup_experiments(backend):    
  job_files = [f for f in listdir("./fusion_config/experiment_configs") if isfile(join("./fusion_config/experiment_configs", f)) and f.endswith("_experiment.json")]    
  for file in job_files:    
    print ("Creating Experiment for %s" % file)   
    backend.create_experiment(json.load(open(join("./fusion_config/experiment_configs", file))))

# Setup schema for user collection
def setup_user_fields(backend, collection_id):
  backend.add_field(collection_id, "username", type="string", required=True)
  backend.add_field(collection_id, "email", type="string", required=True)
  backend.add_field(collection_id, "password", type="string", required=True)
  backend.add_field(collection_id, "first_name", type="string", required=True)
  backend.add_field(collection_id, "last_name", type="string", required=True)

# Loop over the Fusion config and add any pipelines defined there.
def setup_pipelines(backend):
  pipe_files = [f for f in listdir("./fusion_config/pipeline_configs") if isfile(join("./fusion_config/pipeline_configs", f)) and f.endswith("_pipeline.json")]
  for file in pipe_files:
    print ("Creating Pipeline for %s" % file)
    if file.find("query") != -1:
      backend.create_pipeline(json.load(open(join("./fusion_config/pipeline_configs", file))), pipe_type="query-pipelines")
    else:
      backend.create_pipeline(json.load(open(join("./fusion_config/pipeline_configs", file))))

# Loop over batch jobs in the fusion config and add any jobs defined there 
def setup_batch_jobs(backend):
  job_files = [f for f in listdir("./fusion_config/job_configs") if isfile(join("./fusion_config/job_configs", f)) and f.endswith("_job.json")]
  for file in job_files:
    print ("Creating Job for %s" % file)
    backend.create_batch_job(json.load(open(join("./fusion_config/job_configs", file))))

# Create the taxonomy, which can be used to alter requests based on hierarchy
def setup_taxonomy(backend, collection_id):
  status = backend.delete_taxonomy(collection_id)
  taxonomy = json.load(open('fusion_config/taxonomy.json'))
  status = backend.create_taxonomy(collection_id, taxonomy)

# Schedule all non-datasource by looking in fusion_config for schedule declarations
def setup_schedules(backend):
  files = [f for f in listdir("./fusion_config/schedule_configs") if isfile(join("./fusion_config/schedule_configs", f)) and f.endswith("_schedule.json")]
  for file in files:
    print("Creating Schedule for %s" % file)
    backend.create_or_update_schedule(json.load(open(join("./fusion_config/schedule_configs", file))))

# bootstrap.py --start_schedules
def start_schedules(backend):
  backend.activate_schedules()

# bootstrap.py --stop_schedules
def stop_schedules(backend):
  backend.stop_schedules()

def stop_datasources(backend):
  backend.stop_datasources()

# Map the project_config directory into Fusion datasources and schedules.
def setup_projects(backend):
  project_files = [f for f in listdir("./project_config") if isfile(join("./project_config", f)) and f.endswith(".json")]
  if cmd_args.start_datasources:
    print("Each data source created will also be started")
  else:
    print("")
    print("Skipping starting the datasources.  Pass in --start_datasources if you wish to start them when bootstrapping")

  for file in project_files: #TODO: what's the python way here?
    print ("Creating Project for %s" % file)
    project = json.load(open(join("./project_config", file)))
    print("Bootstrapping configs for %s..." % project["name"])
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

def setup_typeahead_collection(backend):
  print ("Creating typeahead collection ")
  collection_id = "shub-typeahead"
  status = backend.create_collection("shub-typeahead", enable_signals=False, enable_search_logs=False, enable_dynamic_schema=False)
  if status == False:
    exit(1)
    
  files = [f for f in listdir("./typeahead_config") if isfile(join("./typeahead_config", f)) and f.endswith("_field_type.json")]
  for file in files:
    print ("Creating typeahead field_type for %s" % file)
    backend.add_field_type("shub-typeahead", json.load(open(join("./typeahead_config", file))))

  pipe_files = [f for f in listdir("./typeahead_config") if isfile(join("./typeahead_config", f)) and f.endswith("_pipeline.json")]
  for file in pipe_files:
    print ("Creating Pipeline for %s" % file)
    if file.find("query") != -1:
      backend.create_pipeline(json.load(open(join("./typeahead_config", file))), pipe_type="query-pipelines")
    else:
      backend.create_pipeline(json.load(open(join("./typeahead_config", file))))

  backend.add_field(collection_id, "name_contains", type="ngram", stored="true", multivalued="false")
  backend.add_field(collection_id, "name_edge", type="edge_ngram", stored="true", multivalued="false")
  backend.add_field(collection_id, "name_en", type="text_en", stored="true", multivalued="false")
  backend.add_field(collection_id, "name_no_vowels", type="text_no_vowels", stored="true", multivalued="false")
  backend.add_field(collection_id, "name_phonetic_en", type="phonetic_en", stored="true", multivalued="false")
  backend.add_field(collection_id, "name_sort", type="string_sort", stored="false", multivalued="false")
  backend.add_field(collection_id, "spell", type="text_general", stored="false", multivalued="false")
  
  backend.add_field(collection_id, "name", type="text_general", multivalued="false", stored="true", copyDests=["name_edge", "name_contains", "name_no_vowels", "name_phonetic_en", "name_en", "name_sort", "spell"])
  backend.add_field(collection_id, "type", type="string", stored="true")
  backend.add_field(collection_id, "synonyms", type="text_general", stored="true", multivalued="true")
  backend.add_field(collection_id, "bh_search_score", type="int", stored="true")
  backend.add_field(collection_id, "bh_rank", type="int", stored="true")
  backend.add_field(collection_id, "productVersion", type="string", stored="true")
  backend.add_field(collection_id, "resourceName", type="string", multivalued="true")
  print ("Finished creating fields")

def setup_typeahead_datasource(backend):
  print ("Creating typeahead datasource")
  datasource_files = [f for f in listdir("./typeahead_config") if isfile(join("./typeahead_config", f)) and f.endswith("_datasource.json")]
  fusion_update_url = app.config['FUSION_URLS'][0] + "apollo/connectors/datasources"
  FUSION_USERNAME = app.config.get("FUSION_ADMIN_USERNAME", "admin")
  FUSION_PASSWORD = app.config.get("FUSION_ADMIN_PASSWORD")
  for file in datasource_files:
    resp = requests.post(fusion_update_url,
                                 data=json.dumps(json.load(open(join("./typeahead_config", file)))),
                                 headers={'Content-type': 'application/json'},
                                 auth=(FUSION_USERNAME, FUSION_PASSWORD))
  print ("Finished creating datasource")

# ------------------------------------------------------------------------------------------------ # 
# ACTUAL WORK 

# Setting the system metrics and logging level 
backend.toggle_system_metrics(False)
backend.set_log_level("WARN")

# Updating the logging schedule to delete logs when appropriate 
backend.update_logging_scheduler()

# Setting up the variables we will be using that are user related
lucidfind_collection_id = app.config.get("FUSION_COLLECTION", "lucidfind")
lucidfind_batch_recs_collection_id = app.config.get("FUSION_BATCH_RECS_COLLECTION", "lucidfind_thread_recs")
user_collection_id = app.config.get("USER_COLLECTION", "users")
username = app.config.get("FUSION_APP_USER", "lucidfind")

# Updating the permissions for the search user 
# TODO: Make this less gross. This is pretty ugly right now. 
if cmd_args.create_collections or create_all:
  update_permissions = {
    "permissions": [
      {
        "methods": [
          "GET"
        ],
        "path": "/query-pipelines/query-similarities/collections/query-similarities/select"
      },
      {
        "methods": [
          "GET"
        ],
        "path": "/query-pipelines/query-recommendation-matching/collections/query-recommendation-matching/select"
      },
      {
        "methods": [
          "GET"
        ],
        "path": "/query-pipelines/query-similarities/collections/query-similarities/suggest"
      },
      {
        "methods": [
          "GET"
        ],
        "path": "/query-pipelines/query-recommendation-matching/collections/query-recommendation-matching/suggest"
      },
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
        "path": "/query-pipelines/typeahead_test-grouped/collections/shub-typeahead/select".format(lucidfind_collection_id)
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
        "path": "/query-pipelines/site-search-blog/collections/{0}/select".format(lucidfind_collection_id)
      },
      {
        "methods": [
          "GET"
        ],
        "path": "/query-pipelines/site-search-support/collections/{0}/select".format(lucidfind_collection_id)
      },
      {
        "methods": [
          "GET"
        ],
        "path": "/query-pipelines/site-search-documentation/collections/{0}/select".format(lucidfind_collection_id)
      },
      {
        "methods": [
          "GET"
        ],
        "path": "/query-pipelines/site-search-videos/collections/{0}/select".format(lucidfind_collection_id)
      },
      {
        "methods": [
          "GET"
        ],
        "path": "/query-pipelines/site-search-all/collections/{0}/select".format(lucidfind_collection_id)
      },
      {
        "methods": [
          "GET"
        ],
        "path": "/query-pipelines/site-search-all/collections/{0}/get".format(lucidfind_collection_id)
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

# Adding the appropriate (lucidfind) user 
status = backend.create_user(username, app.config.get("FUSION_APP_PASSWORD"))
if status == False:
  exit(1)

# Creating the lucidfind collection and its request handlers 
if cmd_args.create_collections or create_all:
  # Setting shard, replica and solr param variables
  num_shards = app.config.get("FUSION_COLLECTION_NUM_SHARDS", "1")
  num_replicas = app.config.get("FUSION_COLLECTION_NUM_REPLICAS", "2")
  solr_params = {"replicationFactor":int(num_replicas),"numShards":int(num_shards)}

  # Creating the lucidfind collection
  status = backend.create_collection(lucidfind_collection_id, enable_signals=True, solr_params=solr_params, default_commit_within=60*10*1000)
  if status == False:
    exit(1)

  # Set up request handlers 
  # DEPRECATED: Due to a bug in Solr around suggesters, let's try to remove the suggester first
  # backend.remove_request_handler(lucidfind_collection_id, "/suggest")
  # backend.remove_search_component(lucidfind_collection_id, "suggest")
  setup_field_types(backend, lucidfind_collection_id)
  setup_find_fields(backend, lucidfind_collection_id)
  setup_request_handlers(backend, lucidfind_collection_id)
  setup_commit_times(backend, lucidfind_collection_id)
  setup_commit_times(backend, "logs", 5*60*1000)
  setup_commit_times(backend, "lucidfind_logs", 5*60*1000)
  status = backend.create_collection("lucidfind_thread_recs")
  if status == False:
    exit(1)

  # Creating the "users" collection for registration
  status = backend.create_collection(user_collection_id, enable_signals=False, enable_search_logs=False, enable_dynamic_schema=False)
  if status == False:
    exit(1)
  setup_user_fields(backend, user_collection_id)
  
  # Creating the collection we will be using for weights aggregation
  status = backend.create_collection("lucidfind_email_subject_weights", enable_signals=False, enable_search_logs=False, enable_dynamic_schema=False)
  if status == False: 
    exit(1)

  # Creating the collection we will be using for the recommendations 
  status = backend.create_collection("lucidfind_subjects_for_emails", enable_signals=False, enable_search_logs=False, enable_dynamic_schema=False)
  status = backend.create_collection("lucidfind_subjects_for_subjects", enable_signals=False, enable_search_logs=False, enable_dynamic_schema=False)

# Creating the pipelines and profiles 
if cmd_args.create_pipelines or create_all:
  setup_pipelines(backend)
  backend.create_query_profile(lucidfind_collection_id, "lucidfind-default", "lucidfind-default")
  backend.create_query_profile(lucidfind_collection_id, "site-search-blog", "site-search-blog")
  backend.create_query_profile(lucidfind_collection_id, "site-search-documentation", "site-search-documentation")
  backend.create_query_profile(lucidfind_collection_id, "site-search-support", "site-search-support")
  backend.create_query_profile(lucidfind_collection_id, "site-search-videos", "site-search-videos")
  backend.create_query_profile(lucidfind_collection_id, "site-search-all", "site-search-all")

# Creating the taxonomy
if cmd_args.create_taxonomy or create_all:
  setup_taxonomy(backend, lucidfind_collection_id)

# Configuring each Project.
if cmd_args.create_projects or create_all:
  setup_projects(backend)

# Setting up recommender and aggregation for recommender jobs
if cmd_args.create_batch_jobs or create_all:
 setup_batch_jobs(backend)

# Creating the schedules
if cmd_args.create_schedules or create_all:
  setup_schedules(backend)

# Creating the experiments 
if cmd_args.create_experiments or create_all:
  setup_experiments(backend)
  
# Creating the typeahead collection 
if cmd_args.create_typeahead_collection:
  collection_id = "shub-typeahead"
  status = backend.create_collection("shub-typeahead", enable_signals=False, enable_search_logs=False, enable_dynamic_schema=False)
  if status == False:
    exit(1)
    
  files = [f for f in listdir("./typeahead_config") if isfile(join("./typeahead_config", f)) and f.endswith("_field_type.json")]
  for file in files:
    print ("Creating typeahead field_type for %s" % file)
    backend.add_field_type("shub-typeahead", json.load(open(join("./typeahead_config", file))))

  pipe_files = [f for f in listdir("./typeahead_config") if isfile(join("./typeahead_config", f)) and f.endswith("_pipeline.json")]
  for file in pipe_files:
    print ("Creating Pipeline for %s" % file)
    if file.find("query") != -1:
      backend.create_pipeline(json.load(open(join("./typeahead_config", file))), pipe_type="query-pipelines")
    else:
      backend.create_pipeline(json.load(open(join("./typeahead_config", file))))
      
  print ("Creating fields")
  backend.add_field(collection_id, "name_contains", type="ngram", stored="true", multivalued="false")
  backend.add_field(collection_id, "name_edge", type="edge_ngram", stored="true", multivalued="false")
  backend.add_field(collection_id, "name_en", type="text_en", stored="true", multivalued="false")
  backend.add_field(collection_id, "name_no_vowels", type="text_no_vowels", stored="true", multivalued="false")
  backend.add_field(collection_id, "name_phonetic_en", type="phonetic_en", stored="true", multivalued="false")
  backend.add_field(collection_id, "name_sort", type="string_sort", stored="false", multivalued="false")
  backend.add_field(collection_id, "spell", type="text_general", stored="false", multivalued="false")
  
  backend.add_field(collection_id, "name", type="text_general", multivalued="false", stored="true", copyDests=["name_edge", "name_contains", "name_no_vowels", "name_phonetic_en", "name_en", "name_sort", "spell"])
  backend.add_field(collection_id, "type", type="string", stored="true")
  backend.add_field(collection_id, "synonyms", type="text_general", stored="true", multivalued="true")
  backend.add_field(collection_id, "bh_search_score", type="int", stored="true")
  backend.add_field(collection_id, "bh_rank", type="int", stored="true")
  backend.add_field(collection_id, "productVersion", type="string", stored="true")
  backend.add_field(collection_id, "resourceName", type="string", multivalued="true")
  print ("Finished creating fields")
  
  print ("Creating datasource")
  datasource_files = [f for f in listdir("./typeahead_config") if isfile(join("./typeahead_config", f)) and f.endswith("_datasource.json")]
  fusion_update_url = app.config['FUSION_URLS'][0] + "apollo/connectors/datasources"
  FUSION_USERNAME = app.config.get("FUSION_ADMIN_USERNAME", "admin")
  FUSION_PASSWORD = app.config.get("FUSION_ADMIN_PASSWORD")
  for file in datasource_files:
    resp = requests.post(fusion_update_url,
                                 data=json.dumps(json.load(open(join("./typeahead_config", file)))),
                                 headers={'Content-type': 'application/json'},
                                 auth=(FUSION_USERNAME, FUSION_PASSWORD))
  print ("Finished creating datasource")

# ***********************************************************************
# Start of query similarity module
if cmd_args.setup_query_recommendations:
  # collection id changed and the folder from where the files are loaded. Rest is the same.
  collection_id = "query-recommendation-matching"
  status = backend.create_collection(collection_id, enable_signals=False, enable_search_logs=False, enable_dynamic_schema=False)
  if status == False:
    exit(1)

  status = backend.create_collection("query-similarities", enable_signals=False, enable_search_logs=False, enable_dynamic_schema=False)
  if status == False:
    exit(1)
    
  files = [f for f in listdir("./query-recommendation_config") if isfile(join("./query-recommendation_config", f)) and f.endswith("_field_type.json")]
  for file in files:
    print ("Creating typeahead field_type for %s" % file)
    backend.add_field_type(collection_id, json.load(open(join("./query-recommendation_config", file))))

  pipe_files = [f for f in listdir("./query-recommendation_config") if isfile(join("./query-recommendation_config", f)) and f.endswith("_pipeline.json")]
  for file in pipe_files:
    print ("Creating Pipeline for %s" % file)
    if file.find("query") != -1:
      backend.create_pipeline(json.load(open(join("./query-recommendation_config", file))), pipe_type="query-pipelines")
    else:
      backend.create_pipeline(json.load(open(join("./query-recommendation_config", file))))

  # set the fields to ngram_query and edge_ngram_query to enable handling typos in queries.
  print ("Creating fields")
  backend.add_field(collection_id, "name_contains", type="ngram_query", stored="true", multivalued="false")
  backend.add_field(collection_id, "name_edge", type="edge_ngram_query", stored="true", multivalued="false")
  backend.add_field(collection_id, "name_en", type="text_en", stored="true", multivalued="false")

  backend.add_field(collection_id, "name", type="text_general", multivalued="false", stored="true", copyDests=["name_edge", "name_contains", "name_en"])
  print ("Finished creating fields")
  
  # change of the path where files are located. i.e. ./query-recommendation_config
  print ("Creating datasource")
  datasource_files = [f for f in listdir("./query-recommendation_config") if isfile(join("./query-recommendation_config", f)) and f.endswith("_datasource.json")]
  fusion_update_url = app.config['FUSION_URLS'][0] + "apollo/connectors/datasources"
  print ("Fusion update url:",fusion_update_url)
  FUSION_USERNAME = app.config.get("FUSION_ADMIN_USERNAME", "admin")
  FUSION_PASSWORD = app.config.get("FUSION_ADMIN_PASSWORD")
  print ("username:",FUSION_USERNAME,"password:",FUSION_PASSWORD)
  for file in datasource_files:
    print ("file:",file)
    resp = requests.post(fusion_update_url,
                                 data=json.dumps(json.load(open(join("./query-recommendation_config", file)))),
                                 headers={'Content-type': 'application/json'},
                                 auth=(FUSION_USERNAME, FUSION_PASSWORD))
  print ("Finished creating datasource")

  print ("Creating spark job")
  job_files = [f for f in listdir("./query-recommendation_config") if isfile(join("./query-recommendation_config", f)) and f.endswith("_job.json")]
  fusion_update_url = app.config['FUSION_URLS'][0] + "apollo/spark/configurations"
  print ("Fusion update url:",fusion_update_url)
  for file in job_files:
      print ("file:",file)
      resp = requests.post(fusion_update_url,
                                   data=json.dumps(json.load(open(join("./query-recommendation_config", file)))),
                                   headers={'Content-type': 'application/json'},
                                   auth=(FUSION_USERNAME, FUSION_PASSWORD))
  print ("Finished creating spark jobs")
  print ("Pipelines and collection setup for the query-recommendation")
  print ("*************************************\nCrawl the datasource and run query-recommendation job!\n*************************************")
  # end of the query-recommendation module
  setup_typeahead_collection(backend)
  setup_typeahead_datasource(backend)
 
# Starting/Stopping the schedules and datasources using the bootstrap   
if cmd_args.start_schedules:
  start_schedules(backend)

if cmd_args.stop_schedules:
  stop_schedules(backend)

if cmd_args.stop_datasources:
  stop_datasources(backend)
