'''
Helper class for creating Github data sources
'''
from server import app
from schedule_helper import create_schedule

def create_github_datasource_configs(project):
  pipeline = project["github_pipeline"]
  if pipeline is None:
    pipeline = "github-default"
  configs = []  # TODO: should we have one crawler for all the repos under this project or one crawler per repo?
  schedules = []
  for repo in project["githubs"]:
    config, schedule = create_config(project["name"], pipeline, repo)
    configs.append(config)
    schedules.append(schedule)

  return configs, schedules


def create_config(project_name, pipeline, repo):
  if "pipeline" in repo:
    pipeline = repo["pipeline"]  # individual mailing lists may override
  config = {"id": "github-{0}-{1}".format(project_name, repo["name"]),
            "connector": "lucid.anda",
            "type": "github",
            "pipeline": pipeline,
            "properties": {
              "collection": "lucidfind",  # TODO: don't hardcode
              "startLinks": [repo["url"]],
              "f.blobs": repo.get("blobs", True),
              "f.branches": repo.get("branches", True),
              "f.commits": repo.get("commits", False),
              "f.issues": repo.get("issues", False),
              "f.pull_requests": repo.get("pull_requests", False),
              "f.pull_request_comments": repo.get("pull_request_comments", False),
              "f.milestones": repo.get("milestones", False),
              "f.commit_diffs": repo.get("commit_diffs", False),
              "f.releases": repo.get("releases", False),
              "fetchThreads": 1
            }
          }

  if "github_user" in repo:
    config['properties']["f.github_username"] = repo["github_user"]
    config['properties']["f.github_password"] = app.config.get(repo["github_pass"])  # TODO: encrypt

  if "includes" in repo:
    config['properties']['includeRegexes'] = [repo["includes"]]

  if "excludes" in repo:
    config['properties']['excludeRegexes'] = [repo["excludes"]]
  schedule = None
  if "schedule" in repo:
    details = repo["schedule"]
    schedule = create_schedule(details, config["id"])
  return config, schedule
