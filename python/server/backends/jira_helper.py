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
                  "enable_security_trimming": False},
                  "initial_mapping": {
                      "id": "FromMap",
                      "mappings": [
                          {"source": "project", "target": project["name"], "operation": "set"},
                          {"source": "project_label", "target": project["label"], "operation": "set"},
                          {"source": "datasource_label", "target": jira["label"], "operation": "set"},
                          {"source": "isBot", "target": "false", "operation": "set"},
                          {
                              "source": "charSet",
                              "target": "charSet_s",
                              "operation": "move"
                          },
                          {
                              "source": "fetchedDate",
                              "target": "fetchedDate_dt",
                              "operation": "move"
                          },
                          {
                              "source": "lastModified",
                              "target": "lastModified_dt",
                              "operation": "move"
                          },
                          {
                              "source": "signature",
                              "target": "dedupeSignature_s",
                              "operation": "move"
                          },
                          {
                              "source": "contentSignature",
                              "target": "signature_s",
                              "operation": "move"
                          },
                          {
                              "source": "length",
                              "target": "length_l",
                              "operation": "move"
                          },
                          {
                              "source": "mimeType",
                              "target": "mimeType_s",
                              "operation": "move"
                          },
                          {
                              "source": "parent",
                              "target": "parent_s",
                              "operation": "move"
                          },
                          {
                              "source": "owner",
                              "target": "owner_s",
                              "operation": "move"
                          },
                          {
                              "source": "group",
                              "target": "group_s",
                              "operation": "move"
                          }
                      ],
                      "reservedFieldsMappingAllowed": False,
                      "skip": False,
                      "label": "field-mapping",
                      "type": "field-mapping"
                  }
              }
    schedule = None
    if "schedule" in jira:
        details = jira["schedule"]
        schedule = create_schedule(details, config["id"])

    if "jira_user" in jira:
        config['properties']["f.jira_username"] = jira["jira_user"],
        config['properties']["f.jira_password"] = app.config.get(jira["jira_pass"]),
    return (config, schedule)
