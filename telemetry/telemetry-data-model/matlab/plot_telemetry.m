clear;
clc;
close all;

data = readtable("telemetry_log.csv");

time = data.timestamp;
temperature = data.temperature_c;
voltage = data.voltage_v;
current = data.current_a;
sequence = data.sequence;

fprintf("===== TELEMETRY SUMMARY METRICS =====\n");
fprintf("Maximum temperature : %.2f °C\n", max(temperature));
fprintf("Minimum temperature : %.2f °C\n", min(temperature));
fprintf("Average temperature : %.2f °C\n", mean(temperature));
fprintf("Maximum voltage     : %.2f V\n",  max(voltage));
fprintf("Minimum voltage     : %.2f V\n",  min(voltage));
fprintf("=====================================\n\n");

figure;
plot(time, temperature, "-o");
xlabel("Timestamp");
ylabel("Temperature (°C)");
title("Telemetry Temperature");
grid on;

figure;
plot(time, voltage, "-o");
xlabel("Timestamp");
ylabel("Voltage (V)");
title("Telemetry Voltage");
grid on;

figure;
plot(time, current, "-o");
xlabel("Timestamp");
ylabel("Current (A)");
title("Telemetry Current");
grid on;

figure;
plot(time, sequence, "-o");
xlabel("Timestamp");
ylabel("Sequence");
title("Telemetry Sequence");
grid on;