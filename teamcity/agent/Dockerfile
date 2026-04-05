FROM jetbrains/teamcity-agent:latest

USER root

# Only install required tools
RUN apt-get update && \
    apt-get install -y curl jq && \
    rm -rf /var/lib/apt/lists/*

USER buildagent