import sys
sys.argv.append('--config')
sys.argv.append('config-docker')
from server import app as application