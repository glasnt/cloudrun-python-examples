# Repo admin

All examples are automatically deployed. 

## Admin Service

This service shows the real-time deployment status of the examples, without having to change each example to self-report. 

## Service Deployment

Triggers are setup so that when the folder is updated in the latest branch, the service re-deploys.

Bulk trigger creation script: 

```
for d in */ ; do
SERVICE=${d%/}
gcloud beta builds triggers create github \
  --repo-owner glasnt \
  --repo-name cloudrun-python-examples \
  --branch-pattern "^latest\$" \
  --build-config cloudbuild.yaml \
  --included-files "${SERVICE}/**" \
  --description ${SERVICE} \
  --substitutions _SERVICE=${SERVICE}
done
```
