#include "telemetry_parser.h"

#define TELEMETRY_PACKET_SIZE 13

int parse_telemetry(
    const uint8_t *buffer,
    uint16_t length,
    TelemetryPacket *packet
)
{
    if (buffer == 0 || packet == 0)
        return 0;

    if (length != TELEMETRY_PACKET_SIZE)
        return 0;

    packet->spacecraft_id = buffer[0];

    packet->timestamp =
        ((uint32_t)buffer[1]) |
        ((uint32_t)buffer[2] << 8) |
        ((uint32_t)buffer[3] << 16) |
        ((uint32_t)buffer[4] << 24);

    packet->temperature_raw =
        (int16_t)(
            ((uint16_t)buffer[5]) |
            ((uint16_t)buffer[6] << 8)
        );

    packet->voltage_raw =
        ((uint16_t)buffer[7]) |
        ((uint16_t)buffer[8] << 8);

    packet->current_raw =
        ((uint16_t)buffer[9]) |
        ((uint16_t)buffer[10] << 8);

    packet->sequence =
        ((uint16_t)buffer[11]) |
        ((uint16_t)buffer[12] << 8);

    return 1;
}