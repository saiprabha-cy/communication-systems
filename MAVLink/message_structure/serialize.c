#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>

#define MAVLINK_V2_STX       0xFD
#define MAVLINK_V2_HEADER_LEN 10U
#define MAVLINK_V2_CHECKSUM_LEN 2U
#define MAX_PAYLOAD_LEN      255U
#define MAX_PACKET_LEN       280U

typedef struct
{
    uint8_t sequence;
    uint8_t system_id;
    uint8_t component_id;
    uint32_t message_id;
    uint8_t payload_length;
    uint8_t payload[MAX_PAYLOAD_LEN];
} mav_message_t;

bool mavlink_serialize(const mav_message_t *msg,
                       uint8_t *packet,
                       uint16_t capacity,
                       uint16_t *packet_length)
{
    if (msg == NULL || packet == NULL || packet_length == NULL)
        return false;

    if (msg->message_id > 0xFFFFFFU)
        return false;

    uint16_t total = MAVLINK_V2_HEADER_LEN
                   + msg->payload_length
                   + MAVLINK_V2_CHECKSUM_LEN;

    if (capacity < total)
        return false;

    packet[0] = MAVLINK_V2_STX;
    packet[1] = msg->payload_length;
    packet[2] = 0x00; /* Incompatibility flags */
    packet[3] = 0x00; /* Compatibility flags */
    packet[4] = msg->sequence;
    packet[5] = msg->system_id;
    packet[6] = msg->component_id;

    /* 24-bit message ID: least significant byte first */
    packet[7] = (uint8_t)(msg->message_id);
    packet[8] = (uint8_t)(msg->message_id >> 8);
    packet[9] = (uint8_t)(msg->message_id >> 16);

    for (uint16_t i = 0; i < msg->payload_length; i++)
        packet[MAVLINK_V2_HEADER_LEN + i] = msg->payload[i];

    /* Placeholder only: MAV-04 will calculate the real CRC */
    packet[total - 2] = 0x00;
    packet[total - 1] = 0x00;

    *packet_length = total;
    return true;
}

int main(void)
{
    mav_message_t msg = {0};

    msg.sequence = 7;
    msg.system_id = 1;
    msg.component_id = 1;
    msg.message_id = 0x123456;
    msg.payload_length = 3;

    msg.payload[0] = 0xAA;
    msg.payload[1] = 0xBB;
    msg.payload[2] = 0xCC;

    uint8_t packet[MAX_PACKET_LEN];
    uint16_t packet_length = 0;

    if (!mavlink_serialize(&msg, packet, sizeof(packet),
                           &packet_length))
    {
        printf("Serialization failed\n");
        return 1;
    }

    printf("Serialized packet (%u bytes):\n", packet_length);

    for (uint16_t i = 0; i < packet_length; i++)
        printf("%02X ", packet[i]);

    printf("\n");
    return 0;
}