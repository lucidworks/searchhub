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
@app.route('/api/<path:other>', methods=["GET", "POST", "PUT"])
def proxy_request(other):
    hostname = app.config.get("FUSION_HOST")
    port = int(app.config.get("FUSION_PORT"))
    protocol = app.config.get("FUSION_PROTOCOL", "http")

    user = app.config.get("FUSION_APP_USER")
    password = app.config.get("FUSION_APP_PASSWORD")

    userAndPass = b64encode(user + ":" + password).decode("ascii")
    request_headers = {'Authorization' : 'Basic %s' %  userAndPass}
    content_type = request.headers['Content_Type']
    for h in ["Cookie", "Referer", "X-Csrf-Token", "Accept-Language", "Accept", "User-Agent"]:
        if h in request.headers:
          request_headers[h] = request.headers[h]

    if request.query_string:
      path = "/api/%s?%s" % (other, request.query_string)
    else:
      path = '/api/' + other
    #print request_headers
    #print "proxy req headers: {0}".format(request_headers)
    if request.method == "POST" or request.method == "PUT":
        #print request
        if request.form:
            print "Form"
            form_data = list(iterform(request.form))
            form_data = urllib.urlencode(form_data)
            request_headers["Content-Length"] = len(form_data)
        elif request.stream and content_type == "application/json":
            print "Stream: {0}".format(content_type)
            chunk_size = 1024
            form_data = None
            tmp = ""
            total_read = 0
            max_read = 1024*1024*2
            while total_read < max_read: #this needs to be smarter
                chunk = request.stream.read(chunk_size)
                amt_read = len(chunk)
                if amt_read == 0:
                    break
                tmp += chunk.decode("utf-8")
                total_read += amt_read
            if tmp:
                form_data = tmp
                request_headers['Content-Type'] = content_type
        else:
            form_data = None

    else:
        form_data = None
    r = None
    #print path
    if request.method == "POST":
        r = requests.post("{0}://{1}:{2}{3}".format(protocol, hostname, port, path), data=form_data, headers=request_headers)
    elif request.method == "PUT":
        print form_data
        #print request_headers
        r = requests.put("{0}://{1}:{2}{3}".format(protocol, hostname, port, path), data=form_data, headers=request_headers)
    else:
        r = requests.get("{0}://{1}:{2}{3}".format(protocol, hostname, port, path), headers=request_headers)
    the_content_type = r.headers['content-type']
    #print "CT: " + the_content_type
    flask_response = Response(response=r.iter_content(8192), content_type=the_content_type,
                              status=r.status_code)
    return flask_response



#app.run(debug=DEBUG_FLAG, host='0.0.0.0', port=LISTEN_PORT)
