FROM jetbrains/teamcity-agent:latest

USER root

RUN apt-get update && \
    apt-get install -y docker.io curl jq && \
    rm -rf /var/lib/apt/lists/*

RUN usermod -aG docker buildagent

USER buildagent
