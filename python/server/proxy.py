import httplib
import re
import urllib
import urlparse
import json

from flask import Flask, Blueprint, request, Response, url_for, stream_with_context
from werkzeug.datastructures import Headers
from werkzeug.exceptions import NotFound
from server import app
from base64 import b64encode
import requests
# Basics From https://github.com/ziozzang/flask-as-http-proxy-server/blob/master/proxy.py

proxy = Blueprint('proxy', __name__)
app.register_blueprint(proxy)
# You can insert Authentication here.
#proxy.before_request(check_login)


def iterform(multidict):
    for key in multidict.keys():
        for value in multidict.getlist(key):
            yield (key.encode("utf8"), value.encode("utf8"))

def parse_host_port(h):
    """Parses strings in the form host[:port]"""
    host_port = h.split(":", 1)
    if len(host_port) == 1:
        return (h, 80)
    else:
        host_port[1] = int(host_port[1])
        return host_port


# For RESTful Service
#@proxy.route('/proxy/<host>/<path:file>', methods=["GET", "POST", "PUT", "DELETE"])
@app.route('/api/<path:other>', methods=["GET", "POST"])
def proxy_request(other):
    hostname = app.config.get("FUSION_HOST")
    port = int(app.config.get("FUSION_PORT"))
    protocol = app.config.get("FUSION_PROTOCOL", "http")

    user = app.config.get("FUSION_APP_USER")
    password = app.config.get("FUSION_APP_PASSWORD")

    userAndPass = b64encode(user + ":" + password).decode("ascii")
    request_headers = {'Authorization' : 'Basic %s' %  userAndPass}
    for h in ["Cookie", "Referer", "X-Csrf-Token", "Accept-Language", "Accept", "User-Agent"]:
        if h in request.headers:
          request_headers[h] = request.headers[h]

    if request.query_string:
      path = "/api/%s?%s" % (other, request.query_string)
    else:
      path = '/api/' + other

    print request_headers
    if request.method == "POST" or request.method == "PUT":
        form_data = list(iterform(request.form))
        form_data = urllib.urlencode(form_data)
        request_headers["Content-Length"] = len(form_data)
    else:
        form_data = None
    r = None
    #print path
    if request.method == "POST" or request.method == "PUT":
        r = requests.post("{0}://{1}:{2}{3}".format(protocol, hostname, port, path), data=form_data, headers=request_headers)
    else:
        r = requests.get("{0}://{1}:{2}{3}".format(protocol, hostname, port, path), headers=request_headers)
    the_content_type = r.headers['content-type']
    #print "CT: " + the_content_type
    flask_response = Response(response=r.iter_content(8192), content_type=the_content_type,
                              status=r.status_code)
    return flask_response



#app.run(debug=DEBUG_FLAG, host='0.0.0.0', port=LISTEN_PORT)
