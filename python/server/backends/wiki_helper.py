import json
from schedule_helper import create_schedule

def create_wiki_datasource_configs(project):
  pipeline = project["wiki_pipeline"]
  if pipeline is None:
    pipeline = "wiki-default"
  configs = []
  schedules = []
  #TODO: should we have one crawler for all the websites under this project or one crawler per website?
  for wiki in project["wikis"]:
    config, schedule = create_config(project["name"], project["label"], pipeline, wiki)
    configs.append(config)
    schedules.append(schedule)
  return configs, schedules


def create_config(project_name, project_label, pipeline, wiki):
  if "pipeline" in wiki:
    pipeline = wiki["pipeline"]  # individual mailing lists may override
  config = {
    'id': "wiki-{0}-{1}".format(project_name, wiki["name"]),
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
      "refreshAll": True,
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
          {"source": "datasource_label", "target": wiki["label"], "operation": "set"},
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
        wiki["url"]
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
  if "excludes" in wiki:
    config['properties']['excludeRegexes'] = [wiki["excludes"]]
  schedule = None
  if "schedule" in wiki:
    details = wiki["schedule"]
    schedule = create_schedule(details, config["id"])
  return config, schedule
