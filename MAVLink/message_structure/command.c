#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>

#define FC_SYSTEM_ID       1U
#define FC_COMPONENT_ID    1U

#define MAV_CMD_REQUEST_MESSAGE 512U
#define MAV_MSG_HEARTBEAT       0U

typedef struct
{
    float param[7];
    uint16_t command;
    uint8_t target_system;
    uint8_t target_component;
    uint8_t confirmation;
} command_long_t;

typedef enum
{
    RESULT_ACCEPTED = 0,
    RESULT_DENIED = 2,
    RESULT_UNSUPPORTED = 3
} command_result_t;

static bool is_zero(float value)
{
    return value == 0.0f;
}

static command_result_t handle_command(
    const command_long_t *cmd)
{
    if (cmd == NULL)
        return RESULT_DENIED;

    if (cmd->target_system != FC_SYSTEM_ID ||
        cmd->target_component != FC_COMPONENT_ID)
    {
        printf("Command addressed to another target.\n");
        return RESULT_DENIED;
    }

    if (cmd->command != MAV_CMD_REQUEST_MESSAGE)
    {
        printf("Unsupported command: %u\n", cmd->command);
        return RESULT_UNSUPPORTED;
    }

    /* Only HEARTBEAT requests are supported by this simulator. */
    if (cmd->param[0] != (float)MAV_MSG_HEARTBEAT)
    {
        printf("Requested message is not supported.\n");
        return RESULT_DENIED;
    }

    /* Parameters 2–7 must be zero for this exercise. */
    for (unsigned i = 1; i < 7; i++)
    {
        if (!is_zero(cmd->param[i]))
        {
            printf("Invalid unused parameter %u\n", i + 1);
            return RESULT_DENIED;
        }
    }

    printf("Heartbeat request accepted.\n");
    printf("Simulator would schedule a HEARTBEAT response.\n");

    return RESULT_ACCEPTED;
}

int main(void)
{
    command_long_t cmd = {0};

    cmd.command = MAV_CMD_REQUEST_MESSAGE;
    cmd.target_system = FC_SYSTEM_ID;
    cmd.target_component = FC_COMPONENT_ID;
    cmd.confirmation = 0;

    cmd.param[0] = (float)MAV_MSG_HEARTBEAT;

    command_result_t result = handle_command(&cmd);

    printf("Command result: %u\n", (unsigned)result);

    return 0;
}