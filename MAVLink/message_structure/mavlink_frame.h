#ifndef MAVLINK_FRAME_H
#define MAVLINK_FRAME_H

#include <stdint.h>

#define MAVLINK_V2_STX 0xFD

typedef struct
{
    uint8_t  magic;
    uint8_t  payload_length;
    uint8_t  incompatibility_flags;
    uint8_t  compatibility_flags;
    uint8_t  sequence;
    uint8_t  system_id;
    uint8_t  component_id;

    uint32_t message_id;

    uint8_t payload[255];

    uint16_t checksum;

} mavlink_frame_t;

#endif