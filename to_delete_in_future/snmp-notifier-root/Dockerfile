FROM alpine:3.18

RUN apk add --no-cache net-snmp-tools

COPY send-trap.sh /usr/local/bin/send-trap.sh
RUN chmod +x /usr/local/bin/send-trap.sh

CMD ["tail", "-f", "/dev/null"]
