%% SAT-05: G/T Calculator
clear; clc;

rx_antenna_gain_dBi = 12;
system_noise_temperature_K = 500;

if system_noise_temperature_K <= 0
    error('System noise temperature must be positive.');
end

GT_dB_per_K = rx_antenna_gain_dBi ...
              - 10*log10(system_noise_temperature_K);

fprintf('SAT-05 G/T CALCULATOR\n');
fprintf('Antenna gain: %.2f dBi\n', rx_antenna_gain_dBi);
fprintf('System noise temperature: %.2f K\n', ...
    system_noise_temperature_K);
fprintf('G/T: %.2f dB/K\n', GT_dB_per_K);