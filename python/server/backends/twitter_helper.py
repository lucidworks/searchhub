from server import app
from schedule_helper import create_schedule
import twitter
import json

'''
Helper class for creating Twitter data sources
'''


def create_twitter_datasource_configs(project):
  """
  Generate the Twitter data source config for a given project

  :param project: the project
  :returns: the configuration dictionary
  """
  twitter_consumer_key = app.config.get('TWITTER_CONSUMER_KEY')
  if twitter_consumer_key is None or twitter_consumer_key == "XXXXXXXX":
    print "No Twitter config set, skipping"
    return None

  try:
    twitter_api = twitter.Api(consumer_key=twitter_consumer_key,
                              consumer_secret=app.config.get('TWITTER_CONSUMER_SECRET'),
                              access_token_key=app.config.get('TWITTER_ACCESS_TOKEN'),
                              access_token_secret=app.config.get('TWITTER_TOKEN_SECRET'))
  except:
    print "Unable to connect to Twitter, skipping"
    return None

  config = {
    'id': "twitter-{0}".format(project["name"]),
    'connector': "lucid.twitter.stream",
    'pipeline': project["twitter_pipeline"],
    'type': "twitter_stream",
    'properties': {
      'collection': app.config.get('FUSION_COLLECTION'),
      'consumer_key': twitter_consumer_key,
      'consumer_secret': app.config.get('TWITTER_CONSUMER_SECRET'),
      'access_token': app.config.get('TWITTER_ACCESS_TOKEN'),
      'token_secret': app.config.get('TWITTER_TOKEN_SECRET'),
      'initial_mapping': {
        'mappings': [
          # Add fields
          {"source": "project", "target": project["name"], "operation": "set"},
          {"source": "project_label", "target": project["label"], "operation": "set"},
          {"source": "datasource_label", "target": project["label"] + " Twitter", "operation": "set"},
          {"source": "source_s", "target": "twitter", "operation": "set"},
          {"source": "isBot", "target": "false", "operation": "set"},

          # People names
          {"source": "userName", "target": "person_ss", "operation": "copy"},
          {"source": "userMentionName", "target": "person_ss", "operation": "copy"},
          {"source": "person_ss", "target": "person_t", "operation": "copy"},
          {"source": "userMentionScreenName", "target": "person_t", "operation": "copy"},
          {"source": "userScreenName", "target": "person_t", "operation": "copy"},

          # Author
          {"source": "userName", "target": "author_s", "operation": "move"},
          {"source": "author_s", "target": "author_t", "operation": "copy"},
          {"source": "userScreenName", "target": "author_t", "operation": "copy"},

          # Other stuff
          {"source": "createdAt", "target": "publishedOnDate", "operation": "move"},
          {"source": "tweet", "target": "content_t", "operation": "move"},
          {"source": "tagText", "target": "tags_ss", "operation": "move"},
          {"source": "tags_ss", "target": "tags_t", "operation": "copy"}

        ]
      },
      'filter_follow': [],
      'filter_track': [],
      'filter_locations':[]
    }
  }

  for follow in project["twitter"]["follows"]:
    print follow
    if follow[0] == '@':
      user = twitter_api.GetUser(screen_name=follow)
      #print user.id
      config['properties']['filter_follow'].append("" + str(user.id))
    else:
      config['properties']['filter_track'].append(follow)

  return config
