#include <stdint.h>
#include <stdio.h>
#include <string.h>

#define MAV_STX       0xFD
#define HEADER_LEN    10U
#define MAX_PACKET    280U

#define MSG_HEARTBEAT 0U
#define HEARTBEAT_CRC_EXTRA 50U

static uint16_t crc_accumulate_byte(uint8_t data, uint16_t crc)
{
    uint8_t tmp = data ^ (uint8_t)(crc & 0xFFU);
    tmp ^= (uint8_t)(tmp << 4);

    return (uint16_t)((crc >> 8)
           ^ ((uint16_t)tmp << 8)
           ^ ((uint16_t)tmp << 3)
           ^ ((uint16_t)tmp >> 4));
}

static uint16_t crc_x25(const uint8_t *data, uint16_t length)
{
    uint16_t crc = 0xFFFFU;

    for (uint16_t i = 0; i < length; i++)
        crc = crc_accumulate_byte(data[i], crc);

    return crc;
}

static void put_u32_le(uint8_t *dst, uint32_t value)
{
    dst[0] = (uint8_t)value;
    dst[1] = (uint8_t)(value >> 8);
    dst[2] = (uint8_t)(value >> 16);
    dst[3] = (uint8_t)(value >> 24);
}

static uint16_t mavlink_crc(const uint8_t *packet,
                            uint8_t payload_len,
                            uint8_t crc_extra)
{
    /* CRC covers LEN through payload, but excludes STX. */
    uint16_t count = 9U + payload_len;
    uint16_t crc = crc_x25(&packet[1], count);

    return crc_accumulate_byte(crc_extra, crc);
}

static uint16_t build_heartbeat(uint8_t sequence,
                                uint8_t *packet,
                                uint16_t capacity)
{
    const uint8_t payload_len = 9U;
    const uint16_t total = HEADER_LEN + payload_len + 2U;

    if (capacity < total)
        return 0;

    packet[0] = MAV_STX;
    packet[1] = payload_len;
    packet[2] = 0;   /* Incompatibility flags */
    packet[3] = 0;   /* Compatibility flags */
    packet[4] = sequence;
    packet[5] = 1;   /* System ID */
    packet[6] = 1;   /* Component ID */

    packet[7] = 0;   /* Message ID: HEARTBEAT = 0 */
    packet[8] = 0;
    packet[9] = 0;

    uint8_t *p = &packet[HEADER_LEN];

    put_u32_le(&p[0], 0);  /* custom_mode */
    p[4] = 1;              /* MAV_TYPE: generic */
    p[5] = 0;              /* MAV_AUTOPILOT: generic */
    p[6] = 0;              /* base_mode: not armed */
    p[7] = 4;              /* MAV_STATE: active */
    p[8] = 3;              /* MAVLink version indicator */

    uint16_t crc = mavlink_crc(packet, payload_len,
                               HEARTBEAT_CRC_EXTRA);

    packet[total - 2] = (uint8_t)crc;
    packet[total - 1] = (uint8_t)(crc >> 8);

    return total;
}

int main(void)
{
    uint8_t packet[MAX_PACKET];

    for (uint8_t seq = 0; seq < 5; seq++)
    {
        uint16_t length = build_heartbeat(
            seq, packet, sizeof(packet));

        if (length == 0)
        {
            printf("Heartbeat encoding failed\n");
            return 1;
        }

        printf("HEARTBEAT seq=%u length=%u bytes: ",
               seq, length);

        for (uint16_t i = 0; i < length; i++)
            printf("%02X ", packet[i]);

        printf("\n");
    }

    return 0;
}