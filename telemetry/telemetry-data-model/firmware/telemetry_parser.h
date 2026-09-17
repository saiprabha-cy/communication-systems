#ifndef TELEMETRY_PARSER_H
#define TELEMETRY_PARSER_H

#include <stdint.h>

typedef struct
{
    uint8_t spacecraft_id;
    uint32_t timestamp;
    int16_t temperature_raw;
    uint16_t voltage_raw;
    uint16_t current_raw;
    uint16_t sequence;
} TelemetryPacket;

int parse_telemetry(
    const uint8_t *buffer,
    uint16_t length,
    TelemetryPacket *packet
);

#endif