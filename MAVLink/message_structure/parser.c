#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>

#define MAV_STX        0xFD
#define MAV_HEADER_LEN 10U
#define MAV_CRC_LEN    2U
#define MAV_MAX_PAYLOAD 255U
#define MAV_MAX_PACKET 280U

typedef enum
{
    PARSE_OK,
    PARSE_INCOMPLETE,
    PARSE_INVALID
} parse_status_t;

typedef struct
{
    uint8_t sequence;
    uint8_t system_id;
    uint8_t component_id;
    uint32_t message_id;
    uint8_t payload_length;
    uint8_t payload[MAV_MAX_PAYLOAD];
    uint16_t checksum;
} parsed_message_t;

parse_status_t mavlink_parse_one(
    const uint8_t *stream,
    size_t stream_length,
    parsed_message_t *out,
    size_t *consumed)
{
    if (stream == NULL || out == NULL || consumed == NULL)
        return PARSE_INVALID;

    *consumed = 0;

    /* Find the next MAVLink 2 start marker. */
    size_t start = 0;

    while (start < stream_length && stream[start] != MAV_STX)
        start++;

    if (start == stream_length)
    {
        /* No start marker found: all current bytes are noise. */
        *consumed = stream_length;
        return PARSE_INCOMPLETE;
    }

    /* Need the complete fixed header before reading its fields. */
    if (stream_length - start < MAV_HEADER_LEN)
    {
        *consumed = start;
        return PARSE_INCOMPLETE;
    }

    const uint8_t *p = &stream[start];
    uint8_t payload_length = p[1];

    size_t total = MAV_HEADER_LEN
                 + (size_t)payload_length
                 + MAV_CRC_LEN;

    /* Wait until the complete unsigned frame is available. */
    if (stream_length - start < total)
    {
        *consumed = start;
        return PARSE_INCOMPLETE;
    }

    /* This teaching parser does not support signing or other
       nonzero incompatibility flags. */
    if (p[2] != 0)
    {
        *consumed = start + 1;
        return PARSE_INVALID;
    }

    out->payload_length = payload_length;
    out->sequence = p[4];
    out->system_id = p[5];
    out->component_id = p[6];

    out->message_id = (uint32_t)p[7]
                    | ((uint32_t)p[8] << 8)
                    | ((uint32_t)p[9] << 16);

    memcpy(out->payload, p + MAV_HEADER_LEN, payload_length);

    size_t crc_offset = MAV_HEADER_LEN + payload_length;

    out->checksum = (uint16_t)p[crc_offset]
                  | ((uint16_t)p[crc_offset + 1] << 8);

    *consumed = start + total;
    return PARSE_OK;
}

int main(void)
{
    /* Demonstration frame from MAV-02.
       Checksum is a placeholder, not a valid computed CRC. */
    const uint8_t packet[] = {
        0xFD, 0x03, 0x00, 0x00, 0x07,
        0x01, 0x01, 0x56, 0x34, 0x12,
        0xAA, 0xBB, 0xCC, 0x00, 0x00
    };

    parsed_message_t msg = {0};
    size_t consumed = 0;

    parse_status_t status = mavlink_parse_one(
        packet, sizeof(packet), &msg, &consumed);

    if (status == PARSE_OK)
    {
        printf("Frame structure extracted\n");
        printf("Bytes consumed: %zu\n", consumed);
        printf("Sequence: %u\n", msg.sequence);
        printf("System ID: %u\n", msg.system_id);
        printf("Component ID: %u\n", msg.component_id);
        printf("Message ID: 0x%06X\n",
               (unsigned int)msg.message_id);

        printf("Payload (%u bytes): ",
               msg.payload_length);

        for (size_t i = 0; i < msg.payload_length; i++)
            printf("%02X ", msg.payload[i]);

        printf("\nChecksum field: 0x%04X\n", msg.checksum);
        printf("Note: checksum has NOT been validated.\n");
    }
    else if (status == PARSE_INCOMPLETE)
    {
        printf("Need more bytes\n");
    }
    else
    {
        printf("Invalid or unsupported frame\n");
    }

    return 0;
}