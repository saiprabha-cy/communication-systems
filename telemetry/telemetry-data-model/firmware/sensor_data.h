#ifndef SENSOR_DATA_H
#define SENSOR_DATA_H

#include <stdint.h>

typedef struct
{
    uint16_t sensor_id;
    float temperature_c;
} TemperatureSensor;

typedef struct
{
    uint16_t sensor_id;
    float voltage_v;
} VoltageSensor;

typedef struct
{
    uint16_t sensor_id;
    float current_a;
} CurrentSensor;

typedef struct
{
    TemperatureSensor temperature;
    VoltageSensor voltage;
    CurrentSensor current;
} SensorData;

#endif