import logging
import os
from flask import render_template, send_from_directory
from flask import request, redirect
from server import app, backend
import werkzeug
import urllib

logging.basicConfig(level=logging.INFO)

LOG = logging.getLogger("views.py")


@app.route('/')
def root():
    return render_template('index.html')

# This route is for back compatibility reasons with the old search hub, although it is not 100% just yet, as we don't handle the passed in paths
@app.route('/p:<path:path>')
def apache(path):
    query = request.args.get("q")
    #print "path: '" + path + "' q: '" + query + "'"
    args = {"query": "(q:'{0}',rows:10,start:0,wt:json)".format(query)}
    return redirect("/search?{0}".format(urllib.urlencode(args)))


@app.route('/search')
def search():
    return render_template('index.html')


# Route all Signals from Snowplow accordingly
@app.route('/snowplow/<path:path>', methods=["GET"])
def track_event(path):
    # TODO: put in spam prevention
    app_id = request.args.get("aid")
    signal = request.args

    print "Request"
    print request
    print "app_id:"
    print app_id
    if app_id == "searchHub" and signal:
        coll_id = app.config.get("FUSION_COLLECTION", "lucidfind")
        result = backend.send_signal(coll_id, signal)
    else:
        print "Unable to send signal: app_id: {0}, signal: {1}".format(app_id, signal)
    #Snowplow requires you respond with a 1x1 pixel
    return send_from_directory(os.path.join(app.root_path, 'assets/img/'), 'onebyone.png')

@app.route('/snowplow_post/<path:foo>', methods=["POST"])
def track_post_event(foo):
    # TODO: put in spam prevention
    # NOTE: when POSTing, we can have multiple events per POST
    json_payload = request.get_json()
    data = json_payload["data"]
    for item in data:
        app_id = item["aid"]
        if app_id == "searchHub":
            coll_id = app.config.get("FUSION_COLLECTION", "lucidfind")
            result = backend.send_signal(coll_id, item)
        else:
            print "Unable to send signal: app_id: {0}, signal: {1}".format(app_id, item)
    #Snowplow requires you respond with a 1x1 pixel
    return ""#send_from_directory(os.path.join(app.root_path, 'assets/img/'), 'onebyone.png')


#@app.errorhandler(werkzeug.exceptions.BadRequest)
#def handle_bad_request(e):
#    print "foo"
#    print e
#    return 'bad request!'

@app.route('/templates/<path:path>')
def send_foundation_template(
        path):  # TODO: we shouldn't need this in production since we shouldn't serve static content from Flask
    return send_from_directory(os.path.join(app.root_path, 'templates'), path)
