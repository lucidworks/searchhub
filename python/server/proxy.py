import httplib
import re
import urllib
import urlparse
import json

from flask import Flask, Blueprint, request, Response, url_for
from werkzeug.datastructures import Headers
from werkzeug.exceptions import NotFound
from server import app
from base64 import b64encode


proxy = Blueprint('proxy', __name__)
app.register_blueprint(proxy)
# You can insert Authentication here.
#proxy.before_request(check_login)

# Filters.
HTML_REGEX = re.compile(r'((?:src|action|href)=["\'])/')
JQUERY_REGEX = re.compile(r'(\$\.(?:get|post)\(["\'])/')
JS_LOCATION_REGEX = re.compile(r'((?:window|document)\.location.*=.*["\'])/')
CSS_REGEX = re.compile(r'(url\(["\']?)/')

REGEXES = [HTML_REGEX, JQUERY_REGEX, JS_LOCATION_REGEX, CSS_REGEX]


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

    print "H: '%s' P: %d" % (hostname, port)
    #print "F: '%s'" % (file)
    # Whitelist a few headers to pass on
    #TODO: fix authtentication.  Change to be a search only user
    user = app.config.get("FUSION_PROXY_USERNAME")
    password = app.config.get("FUSION_PROXY_PASSWORD")

    userAndPass = b64encode(user + ":" + password).decode("ascii")
    request_headers = {'Authorization' : 'Basic %s' %  userAndPass}
    #print request.headers
    #request_headers = {}
    for h in ["Cookie", "Referer", "X-Csrf-Token", "Accept-Language", "Accept", "User-Agent"]:
        if h in request.headers:
        #print h
          request_headers[h] = request.headers[h]

    if request.query_string:
      path = "/api/%s?%s" % (other, request.query_string)
    else:
      path = '/api/' + other

    #print "new headers"
    print request_headers
    if request.method == "POST" or request.method == "PUT":
        form_data = list(iterform(request.form))
        form_data = urllib.urlencode(form_data)
        request_headers["Content-Length"] = len(form_data)
    else:
        form_data = None

    conn = httplib.HTTPConnection(hostname, port)
    print "connecting to: %s %i %s" % (hostname, port, path)
    conn.set_debuglevel(10)

    conn.request(request.method, path, body=form_data, headers=request_headers)
    resp = conn.getresponse()
    print resp.status
    # Clean up response headers for forwarding
    d = {}
    response_headers = Headers()
    for key, value in resp.getheaders():
        print "HEADER: '%s':'%s'" % (key, value)
        d[key.lower()] = value
        if key in ["content-length", "connection", "content-type"]:
            continue

        if key == "set-cookie":
            cookies = value.split(",")
            [response_headers.add(key, c) for c in cookies]
        else:
            response_headers.add(key, value)

    # If this is a redirect, munge the Location URL
    if "location" in response_headers:
        redirect = response_headers["location"]
        parsed = urlparse.urlparse(request.url)
        redirect_parsed = urlparse.urlparse(redirect)

        redirect_host = redirect_parsed.netloc
        if not redirect_host:
            redirect_host = "%s:%d" % (hostname, port)

        redirect_path = redirect_parsed.path
        if redirect_parsed.query:
            redirect_path += "?" + redirect_parsed.query

        munged_path = url_for(".proxy_request",
                              host=redirect_host,
                              file=redirect_path[1:])

        url = "%s://%s%s" % (parsed.scheme, parsed.netloc, munged_path)
        response_headers["location"] = url

    # Rewrite URLs in the content to point to our URL schemt.method == " instead.
    # Ugly, but seems to mostly work.
    #root = url_for(".proxy_request", host=host)
    contents = resp.read()
    #print contents
    flask_response = Response(response=contents,
                              status=resp.status,
                              headers=response_headers,
                              content_type=resp.getheader('content-type'))
    return flask_response



#app.run(debug=DEBUG_FLAG, host='0.0.0.0', port=LISTEN_PORT)
