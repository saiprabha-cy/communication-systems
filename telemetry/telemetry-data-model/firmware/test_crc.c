#include <stdio.h>
#include <stdint.h>
#include "crc16.h"

int main(void)
{
    const uint8_t data[] = "123456789";     //In telecommunications, "123456789" is the universal standard test string. Getting 0x29B1 proves your C bit-shifting logic is mathematically correct.

    uint16_t crc = crc16_ccitt(data, 9);

    printf("CRC = 0x%04X\n", crc);

    return 0;
}


//a complete end-to-end data integrity pipeline—implementing error detection at both ends of a space link (spacecraft and ground station) and proving it works.