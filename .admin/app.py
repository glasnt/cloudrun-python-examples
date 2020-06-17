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
    builds = cb.projects().builds().list(projectId=project).execute()
    triggers = cb.projects().triggers().list(projectId=project).execute()

    results = {}
    # TODO(glasnt) cleanup
    for srv in services["items"]:
        name = srv["metadata"]["name"]
        url = srv["status"]["url"]

        if name == "admin":
            continue

        trigger = [
            t for t in triggers["triggers"]
                if "substitutions" in t.keys()
                    and "_SERVICE" in t["substitutions"].keys()
                    and t["substitutions"]["_SERVICE"] == name
        ]
        if trigger:
            trigger = trigger[0]

            last_build = [
                b
                for b in builds["builds"]
                if "buildTriggerId" in b and b["buildTriggerId"] == trigger["id"]
                and "finishTime" in b.keys()
            ]
            if last_build:
                commit_id = last_build[0]["substitutions"]["SHORT_SHA"]
                finishTime = last_build[0]["finishTime"]
                success = last_build[0]["status"] == "SUCCESS"
            else:
                trigger = None
                commit_id = None
                finishTime = None
                success = None
        else:
            trigger = None
            commit_id = None
            finishTime = None
            success = None

        results[name] = {"commit_id": commit_id, "finishTime": finishTime,
                "url": url, "success": success}
    return results


@app.route("/api")
def report():
    return jsonify(run_report())


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
def relative_time(dstr):
    if not dstr:
        return "(no data)"
    delta = dateparser.parse("now Z") - dateparser.parse(dstr, settings={"TIMEZONE": "Z"})
    return f"{format_timedelta(delta)} ago"

@app.route("/status")
def status():
    data = run_report()
    resp = []
    for key in data.keys():
        state = data[key]
        state["name"] = key
        state["relativeFinishTime"] = relative_time(state["finishTime"])
        resp.append(state)
    return render_template("index.html", data=resp)

@app.route("/status/<service>.svg")
def status_image(service):
    data = run_report() # TODO(glasnt) - do a more efficient call
    if service in data.keys():
        result = data[service]

        if result["success"]:
            success_color = "success"
        else:
            success_color = "critical"
        commit_id = result["commit_id"]
    else:
        commit_id = "unknown"
        success_color = "inactive"

    shield_label = "Last sample deployed at commit".replace(" ", "%20")
    shield_url = (f"https://img.shields.io/badge/{shield_label}-{commit_id}-{success_color}"
                   "?style=flat-square&logo=google-cloud&logoColor=white")
    resp = httpx.get(shield_url)
    return Response(resp.content, mimetype="image/svg+xml")

@app.route("/status")
def status_home():
    return str(request.__dict__)


if __name__ == "__main__":
    app.run(host="localhost", port=8080, debug=True)
