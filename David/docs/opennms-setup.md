# OpenNMS Setup and Monitoring

https://github.com/gallenc/opennms-tutorials-1/tree/main/session1/minimal-minion-activemq  docker compose porject with opennms - should work

You need to connect the docker compose network to the containerlab network  https://docs.docker.com/compose/how-tos/networking/
See also containerlab netowrking https://containerlab.dev/manual/network/

```
networks:
  N000:
    ipam:
      config:
        - subnet: 172.20.0.0/24
  N001:
    ipam:
      config:
        - subnet: 172.20.2.0/24

  containerlab:
    name: my-pre-existing-network-containerlab
    external: true

```

## Overview
OpenNMS was deployed using Docker to monitor the Containerlab network environment and detect network events.

## Installation
OpenNMS was started using:
docker run -d --name opennms -p 8980:8980 opennms/horizon:latest

## Device Configuration
Lab devices were added using their container IP addresses.

## Monitoring
ICMP monitoring was used to detect device availability and status.

## Testing
An interface was manually brought down to simulate a fault. OpenNMS successfully detected the change and generated an event.

## Outcome
OpenNMS is successfully integrated as the monitoring component of the system.

## OpenNMS Access Issue
Initial attempt to access OpenNMS via localhost:8980 resulted in connection refusal. This indicated that the container was either not fully initialized or failed to start.

Further troubleshooting involved checking container status and logs.

## OpenNMS Startup Issue
The initial OpenNMS container failed to remain running because it was started with the `-h` option, which only displays the help menu and exits.

## Resolution
The container was removed and restarted using the `-s` option, which initializes the configuration and starts the OpenNMS service.

### Commands used
```bash
docker rm -f opennms
docker run -d --name opennms -p 8980:8980 opennms/horizon:latest -s

## OpenNMS Startup Failure
After correcting the startup option from `-h` to `-s`, the OpenNMS container still exited immediately with exit code 127. This indicated that the startup command inside the container failed to execute correctly.

Further troubleshooting was carried out by inspecting the container logs and startup configuration.

## OpenNMS Database Dependency Issue
OpenNMS failed to start successfully because it could not connect to a PostgreSQL database. The logs showed that the connection to `localhost:5432` was refused during database validation.

## Root Cause
The initial deployment only started the OpenNMS container, but OpenNMS also requires a PostgreSQL database service.

## Resolution
A PostgreSQL container was deployed on the same Docker network as OpenNMS, and the OpenNMS container was reconfigured to connect to that database.

### Commands used
```bash
docker rm -f opennms
docker network create opennms-net

docker run -d \
  --name opennms-db \
  --network opennms-net \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=opennms \
  postgres:14

docker run -d \
  --name opennms \
  --network opennms-net \
  -p 8980:8980 \
  -e POSTGRES_HOST=opennms-db \
  -e POSTGRES_PORT=5432 \
  -e POSTGRES_DATABASE=opennms \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=postgres \
  opennms/horizon:latest -s
