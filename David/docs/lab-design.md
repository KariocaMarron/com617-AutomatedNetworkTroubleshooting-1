# Lab Design

## Topology Overview
The lab environment is designed using a minimal two-node topology:

Router1 -------- Router2

## Design Rationale
This simple topology is sufficient to simulate:

- Interface up/down events
- Neighbour adjacency changes

## Design Justification
A minimal setup is used to:

- Reduce complexity
- Focus on core system functionality
- Support Proof of Concept development

## Planned Testing
The following scenarios will be tested:

- Interface shutdown and recovery
- Neighbour loss and detection
