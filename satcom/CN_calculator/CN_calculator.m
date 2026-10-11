%% SAT-06: Carrier-to-Noise Ratio
clear; clc;

% Reuse the SAT-03 example
f_MHz = 437;
range_km = 1000;

tx_power_W = 1;
tx_gain_dBi = 2;
tx_feeder_loss_dB = 1;

rx_gain_dBi = 12;
rx_feeder_loss_dB = 1;
other_losses_dB = 2;

% Receiver parameters
Tsys_K = 500;
bandwidth_Hz = 25000;

% Boltzmann constant in dBW/K/Hz
k_dBW_per_K_Hz = -228.599;

% Calculate received carrier power
tx_power_dBW = 10*log10(tx_power_W);

EIRP_dBW = tx_power_dBW ...
           + tx_gain_dBi ...
           - tx_feeder_loss_dB;

FSPL_dB = 92.45 ...
          + 20*log10(f_MHz/1000) ...
          + 20*log10(range_km);

Pr_dBW = EIRP_dBW ...
         - FSPL_dB ...
         + rx_gain_dBi ...
         - rx_feeder_loss_dB ...
         - other_losses_dB;

% Thermal noise power
noise_dBW = k_dBW_per_K_Hz ...
            + 10*log10(Tsys_K) ...
            + 10*log10(bandwidth_Hz);

% Carrier-to-noise ratio
CN_dB = Pr_dBW - noise_dBW;

fprintf('SAT-06 C/N CALCULATOR\n');
fprintf('Received carrier power: %.2f dBW\n', Pr_dBW);
fprintf('Thermal noise power: %.2f dBW\n', noise_dBW);
fprintf('C/N: %.2f dB\n', CN_dB);