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

FUSION_PROTOCOL = "http" # Optionally set the protocol, else defaults to http
FUSION_HOST = "localhost"
FUSION_PORT = 8764
FUSION_URL = "http://" + FUSION_HOST + ":" + str(FUSION_PORT) + "/api/"
FUSION_COLLECTION = "lucidfind"


FUSION_ADMIN_USERNAME="admin"
FUSION_ADMIN_PASSWORD="XXXXXX"

FUSION_APP_USER = "lucidfind"
FUSION_APP_PASSWORD = "XXXXX"


APPROVED_HOSTS = set(["localhost:8764"])
CHUNK_SIZE = 1024

# For project datasource that require passwords per instance (i.e. a JIRA password or Github), the helper classes look for a key in this file that contains the password
# instead of putting it unencrypted in the DB.  Eventually this will be replaced by a keystore
#
#JIRA
#jiraKey
# Github
GITHUB_KEY="XXXXXXXX"


# Twitter Config
TWITTER_CONSUMER_KEY = "XXXXXXXX"
TWITTER_CONSUMER_SECRET = "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
TWITTER_ACCESS_TOKEN = "YYYYYYYY"
TWITTER_TOKEN_SECRET = "YYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYY"

ENABLE_SCHEDULES=False
