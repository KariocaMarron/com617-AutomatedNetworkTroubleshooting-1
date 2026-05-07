# Sprint Retrospectives - COM617 MARR Project

Group 15 - Industrial Consulting Project, Cisco Systems sponsor

## Sprint 1 - Lab Foundation (Weeks 1-3)

What worked. The Containerlab + FRRouting topology came up cleanly under
Docker Compose on the team's hardware. Three FRR routers and two minions
registered with OpenNMS Horizon 33.0.2 within five minutes of cold start.
The dual-remote Git workflow (KariocaMarron origin, com617-industrial-2025-1
upstream) was established early and held throughout.

What did not. The minion registration failed silently on the first cold
start because the activemq.properties file was placed in
/opt/opennms/etc/ rather than the supported overlay path
/opt/opennms-overlay/etc/opennms.properties.d/. The fix was a one-line
path correction; the lesson was that OpenNMS overlay semantics are
position-sensitive and our initial assumption was wrong.

Correction taken into Sprint 2. All container-overlay configurations now
land in the documented overlay path; we treat OpenNMS configuration as
opaque and verify behaviour against documented mounts rather than guessing.

## Sprint 2 - Pipeline Stabilisation (Weeks 4-7)

What worked. The Kafka-mediated ingestion pipeline (snmp.traps,
syslog.events, raw.alerts) connected the listeners to the receiver with
no message loss across the tested rate. The rule-based classifier
reached 94% accuracy against a held-out 30-sample-per-class corpus.

What did not. The Diag Status field in the Mattermost reports presented
play rc=0 as an unconditional success indicator, which was misleading
when individual Ansible tasks within a play had failed. We surfaced this
as a fidelity issue at the Sprint 2 review and scoped the fix for Sprint 3.

Correction taken into Sprint 3. Diag Status now surfaces per-task
accounting (e.g. '2/6 ok, 4 failed') rather than collapsing to a single
play return code.

## Sprint 3 - Correlation and In-Session Engineering (Weeks 8-12)

What worked. The Redis-backed correlator was added mid-sprint by
subscribing to existing Kafka topics with no change to the receiver -
direct vindication of the Kafka-over-RabbitMQ decision recorded in
Appendix B.1. The cascade test on 3 May 2026 grouped two of three events
into a single Mattermost report.

What did not. The first cascade test failed because of a window-versus-
lease Redis TTL race condition; the second cascade test then failed
because the correlator did not load .env before importing
mattermost_notifier, so webhook URL capture fell through. Both were
diagnosed and fixed in-session and are documented verbatim in the Lab
Session Log.

Correction taken forward. The blocking-emission limitation surfaced in
the same session is documented as Section 9.4 of the PID and scoped as
v1.1 work. The in-session diagnostic methodology (hypothesis, test,
observation, root-cause, fix, re-test) is now the team's default
debugging discipline.
