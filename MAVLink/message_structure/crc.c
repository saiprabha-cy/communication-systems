#include <stdint.h>
#include <stdio.h>

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

int main(void)
{
    /* Standard CRC-16/X-25 check input: ASCII "123456789". */
    const uint8_t test[] = "123456789";
    uint16_t crc = crc_x25(test, 9);

    printf("CRC-16/X-25 = 0x%04X\n", crc);
    return 0;
}