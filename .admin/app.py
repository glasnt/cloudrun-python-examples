import os
import json

from flask import Flask, jsonify

import google.auth
from googleapiclient.discovery import build

app = Flask(__name__)
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True

_, project = google.auth.default()
region = os.environ.get("REGION", "us-central1")


@app.route("/report")
def report():
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

    for srv in services["items"]:
        name = srv["metadata"]["name"]
        url = srv["status"]["url"]

        if name == "admin":
            continue

        trigger = [
            t for t in triggers["triggers"] if t["substitutions"]["_SERVICE"] == name
        ]
        if trigger:
            trigger = trigger[0]

            last_build = [
                b
                for b in builds["builds"]
                if "buildTriggerId" in b and b["buildTriggerId"] == trigger["id"]
            ][0]
            commit_id = last_build["substitutions"]["SHORT_SHA"]
            finishTime = last_build["finishTime"]
        else:
            trigger = None
            commit_id = None
            finishTime = None

        results[name] = {"commit_id": commit_id, "finishTime": finishTime,
                "url": url}
    return jsonify(results)


@app.route("/")
def home():
    return "Run /report (may take a while)"


if __name__ == "__main__":
    app.run(host="localhost", port=8080, debug=True)
