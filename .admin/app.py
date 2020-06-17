import os
import json
import httpx
from babel.dates import format_timedelta
import dateparser
from flask import Flask, jsonify, request, send_file, render_template, Response

import google.auth
from googleapiclient.discovery import build

app = Flask(__name__, static_url_path='/static', static_folder='static')
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True

_, project = google.auth.default()
region = os.environ.get("REGION", "us-central1")

def run_report():
    run = build("run", "v1")
    services = (
        run.projects()
        .locations()
        .services()
        .list(parent=f"projects/{project}/locations/{region}")
        .execute()
    )

    cb = build("cloudbuild", "v1")

    results = {}
    for srv in services["items"]:
        name = srv["metadata"]["name"]
        url = srv["status"]["url"]

        trigger = None; commit_id = None; finishTime = None; success = None

        if name == "admin":
            continue

        trigger_id = get_trigger_id(cb, name)
        if trigger_id:
            last_build = latest_build(cb, trigger_id)
            if last_build:
                commit_id = last_build["substitutions"]["SHORT_SHA"]
                finishTime = last_build["finishTime"]
                success = last_build["status"] == "SUCCESS"

        results[name] = {"commit_id": commit_id,
                        "finishTime": finishTime,
                         "url": url,
                         "success": success}
    return results

def get_trigger_id(cb, name):
    triggers = cb.projects().triggers().list(projectId=project).execute()
    for t in triggers["triggers"]:
        if "substitutions" not in t.keys():
            continue
        if "_SERVICE" not in t["substitutions"].keys():
            continue
        if t["substitutions"]["_SERVICE"] == name:
            return t["id"]
    return None



def latest_build(cb, trigger_id):
    kwargs = {
                "projectId": project,
                "filter": f'trigger_id="{trigger_id}"',
                "pageSize": 1
            }
    # presumes order
    builds = cb.projects().builds().list(**kwargs).execute()
    if builds:
        return builds["builds"][0]
    else:
        return None


@app.route("/api")
def report():
    return jsonify(run_report())

def relative_time(dstr):
    if not dstr:
        return "(no data)"
    delta = dateparser.parse("now Z") - dateparser.parse(dstr, settings={"TIMEZONE": "Z"})
    return f"{format_timedelta(delta)} ago"

@app.route("/status")
def status():
    data = run_report()

    # converting dict to list, for table formatting ease
    resp = []
    for key in data.keys():
        state = data[key]
        state["name"] = key
        state["relativeFinishTime"] = relative_time(state["finishTime"])
        resp.append(state)
    return render_template("index.html", data=resp)

@app.route("/status/<service>.svg")
def status_image(service):
    cb = build("cloudbuild", "v1")
    commit_id = "unknown"; success_color = "inactive"
    trigger_id = get_trigger_id(cb, service)
    if trigger_id:
        result = latest_build(cb, trigger_id)
        if result:
            if result["status"] == "SUCCESS":
                success_color = "success"
            else:
                success_color = "critical"
            if "substitutions" in result.keys() and "SHORT_SHA" in result["substitutions"].keys():
                commit_id = result["substitutions"]["SHORT_SHA"]
            else:
                commit_id = "unknown"

    shield_label = "Last sample deployed at commit".replace(" ", "%20")
    shield_url = (f"https://img.shields.io/badge/{shield_label}-{commit_id}-{success_color}"
                   "?style=flat-square&logo=google-cloud&logoColor=white")
    resp = httpx.get(shield_url)
    return Response(resp.content, mimetype="image/svg+xml")



@app.route("/")
def home():
    return """<div id='results'><img src="/static/loading.svg"></div>
    <script>
        var xhr = new XMLHttpRequest();
        xhr.open('GET', '/status', true);
        xhr.onreadystatechange = function(e) {
            if (this.readyState == 4) {
                div = document.getElementById("results")
                div.innerHTML = this.responseText;
            }
        };
        xhr.send();
    </script>
    """


if __name__ == "__main__":
    app.run(host="localhost", port=8080, debug=True)
