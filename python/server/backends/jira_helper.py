from server import app
from schedule_helper import create_schedule
'''
Helper class for creating JIRA data sources
'''


def create_jira_datasource_config(project):
  """
  Generate the JIRA data source config for a given project

  :param project: the project
  :returns: the configuration dictionary
  """
  pipeline = project["jira_pipeline"]
  jira = project["jira"]
  if "pipeline" in jira:
    pipeline = jira["pipeline"]
  if pipeline is None:
    pipeline = "jira-default"

  config = {"id": "jira-{0}-{1}".format(project["name"], jira["name"]),
            "connector": "lucid.anda",
            "type": "jira",
            "pipeline": pipeline,
            "properties": {
              "collection": "lucidfind",
              "startLinks": [jira["url"]],
              "enable_security_trimming": False}
            }
  schedule = None
  if "schedule" in jira:
    details = jira["schedule"]
    schedule = create_schedule(details, config["id"])

  if "jira_user" in jira:
    config['properties']["f.jira_username"] = jira["jira_user"],
    config['properties']["f.jira_password"] = app.config.get(jira["jira_pass"]),
  return (config, schedule)
