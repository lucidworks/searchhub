from schedule_helper import create_schedule
from server import app

def create_mailinglist_datasource_configs(project):
  pipeline = project["mailing_list_pipeline"]
  if pipeline is None:
    pipeline = "mailing-list-default"
  configs = []
  schedules = []
  if "mailing_lists" in project:
    for ml in project["mailing_lists"]:
      config, schedule = create_config(project["name"], project["label"], pipeline, ml)
      configs.append(config)
      schedules.append(schedule)
  return configs, schedules


def create_config(project_name, project_label, pipeline, mailing_list):
  if "pipeline" in mailing_list:
    pipeline = mailing_list["pipeline"]  # individual mailing lists may override
  config = {
    'id': "mailing-list-{0}-{1}".format(project_name, mailing_list["name"]),
    "connector": "lucid.anda",
    "type": "web",
    'pipeline': pipeline,
    "properties": {
      "refreshOlderThan": -1,
      "f.appendTrailingSlashToLinks": False,
      "refreshErrors": False,
      "restrictToTreeIgnoredHostPrefixes": [
        "www."
      ],
      "dedupeSaveSignature": False,
      "crawlDBType": "in-memory",
      "f.discardLinkURLQueries": False,
      "f.respectMetaEquivRedirects": False,
      "fetchDelayMS": 50,
      "splitArchives": True,
      "refreshAll": False,
      "refreshScript": "function shouldRefresh(id, depth, lastModified, lastFetched, lastEmitted, error){\n\tvar date = new Date();\n  var month = \"\";\n  if (date.getUTCMonth() < 10){\n    month = \"0\" + (date.getUTCMonth() + 1);\n  } else {\n    month = date.getUTCMonth()  + 1\n  }\n  var yearMonth = date.getUTCFullYear() + \"\" + (month);//need 1 based dates\n  if (id != null){\n    return id.indexOf(yearMonth) != -1\n  }\n  return false;\n}\n",
      "f.defaultMIMEType": "application/octet-stream",
      "restrictToTreeAllowSubdomains": False,
      "maxItems": -1,
      "f.scrapeLinksBeforeFiltering": False,
      "dedupe": False,
      "f.allowAllCertificates": False,
      "collection": "lucidfind",
      "forceRefresh": False,
      "f.obeyRobots": True,
      "fetchDelayMSPerHost": True,
      "indexCrawlDBToSolr": False,
      "fetchThreads": 1,
      "restrictToTree": True,
      "retainOutlinks": True,
      "f.defaultCharSet": "UTF-8",
      "emitThreads": 1,
      "diagnosticMode": False,
      "delete": True,
      "f.userAgentWebAddr": "",
      "initial_mapping": {
        "id": "FromMap",
        "mappings": [
          {"source": "project", "target": project_name, "operation": "set"},
          {"source": "project_label", "target": project_label, "operation": "set"},
          {"source": "datasource_label", "target": mailing_list["label"], "operation": "set"},
          {"source": "fetchedDate", "target": "publishedOnDate", "operation": "copy"},
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
      },
      "restrictToTreeUseHostAndPath": True,
      "f.filteringRootTags": [
        "body",
        "head"
      ],
      "f.userAgentEmail": "",
      "f.timeoutMS": 10000,
      "failFastOnStartLinkFailure": True,
      "startLinks": [
        app.config.get("ASF_MAIL_ARCHIVE_BASE_URL", "http://asfmail.lucidworks.io/mail_files/") + mailing_list["mbox"]
      ],
      "chunkSize": 100,
      "includeRegexes": [],
      "f.obeyRobotsDelay": True,
      "deleteErrorsAfter": -1,
      "f.userAgentName": "Lucidworks-Anda/2.0",
      "retryEmit": True,
      "depth": -1,
      "refreshStartLinks": False,
      "f.maxSizeBytes": 4194304,
      "aliasExpiration": 1
    }
  }
  #automatically exclude date/author sorted links and atom:
  # http://asfmail.lucidworks.io/mail_files/ambari-dev/201412.mbox/date and http://asfmail.lucidworks.io/mail_files/ambari-dev/201412.mbox/author
  # http://asfmail.lucidworks.io/mail_files/ambari-dev/?format=atom
  config['properties']['excludeRegexes'] = [".*/date.*", ".*/author.*", ".*format=atom.*"]
  if "excludes" in mailing_list:
    config['properties']['excludeRegexes'].append(mailing_list["excludes"])
  schedule = None
  if "schedule" in mailing_list:
    details = mailing_list["schedule"]
    schedule = create_schedule(details, config["id"])

  return config, schedule
