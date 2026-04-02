FROM ubuntu:22.04
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update -qq && \
    apt-get install -y python3 python3-pip -qq && \
    pip3 install pysnmp requests && \
    apt-get clean && rm -rf /var/lib/apt/lists/*
WORKDIR /opt
CMD ["sleep", "infinity"]
