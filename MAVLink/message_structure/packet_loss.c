#include <stdint.h>
#include <stdio.h>
#include <stdbool.h>

typedef struct
{
    bool initialized;
    uint8_t last_sequence;
    uint32_t missing_packets;
    uint32_t duplicates;
    uint32_t out_of_order;
    uint32_t received;
} sequence_monitor_t;

static void monitor_packet(sequence_monitor_t *monitor,
                           uint8_t sequence)
{
    if (!monitor->initialized)
    {
        monitor->initialized = true;
        monitor->last_sequence = sequence;
        monitor->received++;

        printf("First packet: seq=%u\n", sequence);
        return;
    }

    uint8_t delta =
        (uint8_t)(sequence - monitor->last_sequence);

    if (delta == 0)
    {
        monitor->duplicates++;
        printf("Duplicate sequence: %u\n", sequence);
        return;
    }

    if (delta == 1)
    {
        printf("Sequence OK: %u\n", sequence);
        monitor->last_sequence = sequence;
        monitor->received++;
        return;
    }

    if (delta < 128)
    {
        uint8_t missing = (uint8_t)(delta - 1U);

        monitor->missing_packets += missing;
        monitor->received++;
        monitor->last_sequence = sequence;

        printf("Sequence gap: received=%u, "
               "potentially missing=%u\n",
               sequence, missing);
        return;
    }

    monitor->out_of_order++;

    printf("Stale/out-of-order or ambiguous packet: %u\n",
           sequence);

    /* Do not move the reference backward for a likely stale packet. */
}

int main(void)
{
    sequence_monitor_t monitor = {0};

    const uint8_t incoming[] = {
        40, 41, 44, 45, 45, 43, 46
    };

    for (unsigned i = 0;
         i < sizeof(incoming) / sizeof(incoming[0]);
         i++)
    {
        monitor_packet(&monitor, incoming[i]);
    }

    printf("\n--- Statistics ---\n");
    printf("Accepted arrivals: %lu\n",
           (unsigned long)monitor.received);
    printf("Potentially missing: %lu\n",
           (unsigned long)monitor.missing_packets);
    printf("Duplicates: %lu\n",
           (unsigned long)monitor.duplicates);
    printf("Out-of-order/ambiguous: %lu\n",
           (unsigned long)monitor.out_of_order);

    return 0;
}