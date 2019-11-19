FROM python:3.7.2-slim-stretch

ENV PYTHONIOENCODING utf-8

COPY . /analyzer
WORKDIR /analyzer
ENV PYTHONPATH=/analyzer/src

RUN pip3 install flake8 flake8-json

# local install
RUN pip3 install -e .


# Setup analysis user for docker
RUN groupadd -r analysis && useradd -m --no-log-init --gid analysis analysis
USER analysis

# Setup entrypoint into the analysis code logic
WORKDIR /
CMD ["/analyzer/analyzer-src/analyze.sh"]
