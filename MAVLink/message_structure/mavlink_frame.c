#include <stdio.h>
#include "mavlink_frame.h"

int main(void)
{
    mavlink_frame_t frame = {0};

    frame.magic = MAVLINK_V2_STX;

    frame.payload_length = 3;

    frame.incompatibility_flags = 0x00;
    frame.compatibility_flags = 0x00;

    frame.sequence = 42;

    frame.system_id = 1;
    frame.component_id = 1;

    frame.message_id = 0x123456;

    frame.payload[0] = 0xAA;
    frame.payload[1] = 0xBB;
    frame.payload[2] = 0xCC;

    frame.checksum = 0x0000;

    printf("MAVLink 2 frame\n");

    printf("STX       : 0x%02X\n", frame.magic);
    printf("Length    : %u\n", frame.payload_length);
    printf("INC flags : 0x%02X\n",
           frame.incompatibility_flags);

    printf("CMP flags : 0x%02X\n",
           frame.compatibility_flags);

    printf("Sequence  : %u\n", frame.sequence);

    printf("System ID : %u\n", frame.system_id);

    printf("Component : %u\n", frame.component_id);

    printf("Message ID: 0x%06X\n",
           frame.message_id);

    printf("Payload   : ");

    for (uint8_t i = 0;
         i < frame.payload_length;
         i++)
    {
        printf("%02X ", frame.payload[i]);
    }

    printf("\n");

    return 0;
}