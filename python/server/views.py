import json
import os
from flask import Response, request, url_for, abort, jsonify
from flask import render_template, send_from_directory
import requests
import base64
from server import app, backend
import logging

logging.basicConfig(level=logging.INFO)


LOG = logging.getLogger("views.py")

@app.route('/')
def root():
  return render_template('index.html')

@app.route('/search')
def search():
    return render_template('index.html')

#[{ "params": {
#      "docId": "2125233",
#      "filterQueries": ["cat00000","abcat0100000", "abcat0101000", "abcat0101001"],
#      "query": "Televisiones Panasonic  50 pulgadas"
#  },
# "type":"click",
# "timestamp": "2011-09-01T23:44:52Z"
#}]
@app.route('/snowplow/<path:path>', methods=["GET"])
def track_event(path):
    #print path
    print request
    app_id = request.args.get("aid")
    platform = request.args.get("p")
    event = request.args.get("e")
    timestamp = request.args.get("dtm")
    print "app: {0} plat: {1} event: {2} time: {3} request: {4}".format(app_id, platform, event, timestamp, request.args)
    if app_id == "searchHub":
      coll_id = app.config.get("FUSION_COLLECTION", "lucidfind")
      result = backend.send_signal(coll_id, request.args)
      #do something if False?

    return send_from_directory(os.path.join(app.root_path, 'assets/img/'), 'onebyone.png')

#@app.route('/snowplow_test')
#def snow():
#    print request
#    return render_template('snowplow.html')

#@app.route('/snowplow_test2')
#def snow2():
#    print request
#    return render_template('snowplow-sync.html')



@app.route('/templates/<path:path>')
def send_foundation_template(path): #TODO: we shouldn't need this in production since we shouldn't serve static content from Flask
    print "template: " + path
    return send_from_directory(os.path.join(app.root_path, 'templates'), path)


@app.route("/documents/<document_id>")
def get_document(document_id):
    doc = backend.get_document(document_id)
    if doc is None:
        abort(404)
    else:
        return Response(json.dumps(doc._asdict(), indent=2), mimetype='application/json')

@app.route("/documents")
def find_documents():
    q = request.args.get("q", "*")
    source = request.args.get("source")
    author = request.args.get("author")
    project = request.args.get("project")
    limit = int(request.args.get("limit", 10))
    offset = int(request.args.get("offset", 0))

    docs, facets, found = backend.find_documents(q, source, author, project, limit, offset)

    filters = {}
    if source is not None:
        filters["source"] = source
    if author is not None:
        filters["author"] = author
    if project is not None:
        filters["project"] = project

    params = request.args

    resp = {
        "href": url_for("find_documents", **params),
        "count": found,
        "offset": offset,
        "limit": limit,
        "items": [doc._asdict() for doc in docs],
        "facets": facets,
        "filters": filters,
        "prev": "",
        "next": ""
    }
    return Response(json.dumps(resp, indent=2), mimetype='application/json')
