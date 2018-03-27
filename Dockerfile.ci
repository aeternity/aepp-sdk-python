# Heads-Up: This Dockerfile is *exclusively* used for CI. It is referenced by
# Jenkinsfile and should not be used by any other means.

FROM python:3-slim

USER root

ADD requirements.txt /
RUN apt-get update && apt-get install build-essential  -y \
	&& pip install -r requirements.txt \
	&& pip install pytest
