import os
# SEE: http://flask.pocoo.org/docs/0.10/config/
# Statement for enabling the development environment
DEBUG = True

# Define the application directory
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# The name and port to bind the server to
# SERVER_NAME = "localhost:5000"

# The backend for the lucidfind application
#BACKEND = "server.backends.mock.MockBackend"
BACKEND = "server.backends.fusion.FusionBackend"

# Application threads. A common general assumption is
# using 2 per available processor cores - to handle
# incoming requests using one and performing background
# operations using the other.
THREADS_PER_PAGE = 2

# Enable protection agains *Cross-site Request Forgery (CSRF)*
CSRF_ENABLED     = True

# Use a secure, unique and absolutely secret key for
# signing the data.
CSRF_SESSION_KEY = "secret"

# Secret key for signing cookies
SECRET_KEY = "secret"

# Fusion Config

# Must be a list and we'll randomly select between them
FUSION_HOSTS = ["localhost", "localhost"]
FUSION_PORTS = [8764, 8764]
FUSION_PROTOCOLS = ["http", "http"]

FUSION_COLLECTION = "lucidfind"
FUSION_COLLECTION_NUM_SHARDS=1
FUSION_COLLECTION_NUM_REPLICAS=2
USER_COLLECTION = "users"

FUSION_ADMIN_USERNAME="admin"
FUSION_ADMIN_PASSWORD="XXXXXX"

FUSION_APP_USER = "lucidfind"
FUSION_APP_PASSWORD = "XXXXX"


APPROVED_HOSTS = set(["localhost:8764"])
CHUNK_SIZE = 1024




# Mail archives location.  Lucidworks offers a mirror of the Apache archives available at "http://asfmail.lucidworks.io/mail_files/"
# The ASF also offers the authoritative version, but it is very easy to get banned from it
ASF_MAIL_ARCHIVE_BASE_URL = "http://asfmail.lucidworks.io/mail_files/"

# FOR USE WITH THE get_youtube.py standalone crawler
# Set DEVELOPER_KEY to the API key value from the APIs & auth > Registered apps
# tab of
#   https://cloud.google.com/console
# Please ensure that you have enabled the YouTube Data API for your project.
YOUTUBE_DEVELOPER_KEY="XXXXXXXXXX"

# For project datasource that require passwords per instance (i.e. a JIRA password or Github), the helper classes look for a key in this file that contains the password
# instead of putting it unencrypted in the DB.  Eventually this will be replaced by a keystore
#
#JIRA
#jiraKey
# Github
# See https://github.com/blog/1509-personal-api-tokens
GITHUB_KEY="XXXXXXXX"


# Twitter Config
# See https://dev.twitter.com/oauth/overview and related documentation on how to obtain these.
TWITTER_CONSUMER_KEY = "XXXXXXXX"
TWITTER_CONSUMER_SECRET = "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
TWITTER_ACCESS_TOKEN = "YYYYYYYY"
TWITTER_TOKEN_SECRET = "YYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYY"

ENABLE_SCHEDULES=False

COMPRESS_MIN_SIZE=125