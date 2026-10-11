#include <stdint.h>
#include <stdio.h>
#include <string.h>

#define MAV_STX        0xFD
#define HEADER_LEN     10U
#define MAX_PACKET     280U

#define MSG_ATTITUDE   30U
#define ATTITUDE_CRC_EXTRA 39U

static uint16_t crc_accumulate_byte(uint8_t data, uint16_t crc)
{
    uint8_t tmp = data ^ (uint8_t)(crc & 0xFFU);
    tmp ^= (uint8_t)(tmp << 4);

    return (uint16_t)((crc >> 8)
           ^ ((uint16_t)tmp << 8)
           ^ ((uint16_t)tmp << 3)
           ^ ((uint16_t)tmp >> 4));
}

static uint16_t mavlink_crc(const uint8_t *packet,
                            uint8_t payload_len,
                            uint8_t crc_extra)
{
    uint16_t crc = 0xFFFFU;

    /* LEN through payload: exclude packet[0], the STX. */
    for (uint16_t i = 1; i < 10U + payload_len; i++)
        crc = crc_accumulate_byte(packet[i], crc);

    return crc_accumulate_byte(crc_extra, crc);
}

static void put_u32_le(uint8_t *dst, uint32_t value)
{
    dst[0] = (uint8_t)value;
    dst[1] = (uint8_t)(value >> 8);
    dst[2] = (uint8_t)(value >> 16);
    dst[3] = (uint8_t)(value >> 24);
}

static void put_float_le(uint8_t *dst, float value)
{
    uint32_t bits;
    memcpy(&bits, &value, sizeof(bits));
    put_u32_le(dst, bits);
}

static uint16_t build_attitude(uint8_t sequence,
                               uint8_t *packet,
                               uint16_t capacity)
{
    const uint8_t payload_len = 28U;
    const uint16_t total = HEADER_LEN + payload_len + 2U;

    if (capacity < total)
        return 0;

    packet[0] = MAV_STX;
    packet[1] = payload_len;
    packet[2] = 0;
    packet[3] = 0;
    packet[4] = sequence;
    packet[5] = 1;
    packet[6] = 1;

    /* ATTITUDE message ID = 30 = 0x00001E */
    packet[7] = 30;
    packet[8] = 0;
    packet[9] = 0;

    uint8_t *p = &packet[HEADER_LEN];

    put_u32_le(&p[0], 12500U);
    put_float_le(&p[4],  0.10f);  /* roll */
    put_float_le(&p[8], -0.05f);  /* pitch */
    put_float_le(&p[12], 1.20f);  /* yaw */
    put_float_le(&p[16], 0.01f);  /* rollspeed */
    put_float_le(&p[20], -0.02f); /* pitchspeed */
    put_float_le(&p[24], 0.03f);  /* yawspeed */

    uint16_t crc = mavlink_crc(packet, payload_len,
                               ATTITUDE_CRC_EXTRA);

    packet[total - 2] = (uint8_t)crc;
    packet[total - 1] = (uint8_t)(crc >> 8);

    return total;
}

int main(void)
{
    uint8_t packet[MAX_PACKET];

    for (uint8_t seq = 0; seq < 5; seq++)
    {
        uint16_t length = build_attitude(
            seq, packet, sizeof(packet));

        if (length == 0)
        {
            printf("Telemetry encoding failed\n");
            return 1;
        }

        printf("ATTITUDE seq=%u length=%u bytes: ",
               seq, length);

        for (uint16_t i = 0; i < length; i++)
            printf("%02X ", packet[i]);

        printf("\n");
    }

    return 0;
}