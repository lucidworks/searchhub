from collections import namedtuple
import importlib

from server import app


class Backend(object):
  "Base class for Backend implementations"

  def __init__(self):
    pass

  def toggle_system_metrics(self, enabled=True):
    raise NotImplementedError()

  def set_log_level(self, logLevel="ERROR"):
    raise NotImplementedError()

  def send_signal(self, collection_id, payload):
    """
    Send a signal
    """
    raise NotImplementedError()

  def get_document(self, doc_id):
    """
    Fetch a single document from the backend

    :param doc_id: the document's id
    :returns: the document or None
    """
    raise NotImplementedError()

  def find_documents(self, query="*", source=None, author=None, project=None, limit=10, offset=0):
    """
    Filter and/or search for documents in the backend

    :param query: a full text query
    :param source: filter on the document's source field
    :param author: filter on the document's author field
    :param author: filter on the document's project field
    :param limit: limits how many results to return
    :param offset: how deeply into the results to start returning
    :returns: a list of the resulting documents
    """
    raise NotImplementedError()

  def create_collection(self, collection_id, enable_signals=False, enable_search_logs=True, enable_dynamic_schema=True, solr_params=None):
    raise NotImplementedError()

  def create_user(self, user, password):
    raise NotImplementedError()

  def create_query_pipeline(self, collection_id, name, pipeline_name):
    raise NotImplementedError()

  def create_taxonomy(self, collection_id, taxonomy):
    raise NotImplementedError()

  def delete_taxonomy(self, collection_id, category=None):
    raise NotImplementedError()

  def create_or_update_project_pipeline(self, project):
    raise NotImplementedError()

  def add_field(self, collection_name, name, type="String", required=False, multivalued=False, indexed=True, stored=True, defaultVal=None):
    raise NotImplementedError()

  def add_field_type(self, collection_name, add_field_json):
    raise NotImplementedError()

  def create_or_update_project(self, project):
    raise NotImplementedError()

  def create_or_update_schedule(self, schedule):
    raise NotImplementedError()

  #if schedules is none, then activate all.  If specified, only activate those schedules that match
  def activate_schedules(self, schedules=None, searchHubOnly=True):
    raise NotImplementedError()

  def stop_schedules(self, schedules=None, searchHubOnly=True):
    raise NotImplementedError()

  def get_role(self, rolename):
    raise NotImplementedError()

  def update_role(self, rolename, data):
    raise NotImplementedError()

  def get_datasource(self, id):
    """
    Retreive a datasource from the backend

    :param id: the datasource's id
    :returns: the datasource or None
    """
    raise NotImplementedError()

  def add_request_handler(self, collection_name, add_req_handler_json):
    raise NotImplementedError()

  def remove_request_handler(self, collection_name, req_handler_name):
    raise NotImplementedError()

  def add_search_component(self, collection_name, add_search_component_json):
    raise NotImplementedError()

  def remove_search_component(self, collection_name, component_name):
    raise NotImplementedError()

  def set_property(self, collection_name, data):
    raise NotImplementedError()

  def unset_property(self, collection_name, data):
    raise NotImplementedError()

  def stop_datasource(self, id, abort=False):
    raise NotImplementedError()

  def stop_datasources(self):
    raise NotImplementedError()

  def update_datasource(self, id, **config):
    """
    Update a datasource in the backend

    :param id: the datasource's id
    :param config: the datasource config as a dictionary
    :returns: the updated datasource
    """
    raise NotImplementedError()

# Some model objects
Document = namedtuple("Document", ["id", "author", "source", "project", "content", "created_at", "link"])


def get_backend():
  "Load the backend impl from config, default to the mock one"
  BACKEND = app.config.get("BACKEND", "server.backends.mock.MockBackend")
  package, clazz = BACKEND.rsplit('.', 1)
  module = importlib.import_module(package)
  return getattr(module, clazz)()
