# Telemetry Data Model

Implementation of TEL-01 from the aerospace embedded/communication roadmap.

## Objective

Define a structured spacecraft telemetry data model that can later be
serialized into binary telemetry packets.

## Current telemetry fields

| Field | Type | Unit |
|---|---|---|
| spacecraft_id | int | - |
| temperature_c | float | °C |
| voltage_v | float | V |
| current_a | float | A |
| battery_percent | float | % |
| sequence | int | - |

## Software

- Python
- dataclasses
- pytest

## Roadmap connection

TEL-01 → Telemetry Data Model  
TEL-02 → Sensor Data Structure  
TEL-03 → Binary Serialization  
TEL-04 → Binary Deserialization  