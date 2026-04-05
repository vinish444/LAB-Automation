FROM jetbrains/teamcity-agent:latest

USER root

# Install only required tools (NO docker.io)
RUN apt-get update && \
    apt-get install -y curl jq ca-certificates && \
    rm -rf /var/lib/apt/lists/*

# Install Docker CLI manually (lightweight, no daemon)
RUN curl -fsSL https://get.docker.com | sh

# Add agent user to docker group
RUN usermod -aG docker buildagent

USER buildagent