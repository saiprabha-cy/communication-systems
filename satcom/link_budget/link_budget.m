%% SAT-03: Satellite Link Budget
clear; clc;

% Inputs
f_MHz = 437;
range_km = 1000;

tx_power_W = 1;
tx_gain_dBi = 2;
tx_feeder_loss_dB = 1;

rx_gain_dBi = 12;
rx_feeder_loss_dB = 1;
other_losses_dB = 2;

% Convert transmitter power to dBW
tx_power_dBW = 10*log10(tx_power_W);

% SAT-04: EIRP
EIRP_dBW = tx_power_dBW + tx_gain_dBi ...
           - tx_feeder_loss_dB;

% Free-space path loss
f_GHz = f_MHz / 1000;

FSPL_dB = 92.45 ...
          + 20*log10(f_GHz) ...
          + 20*log10(range_km);

% Received power
Pr_dBW = EIRP_dBW - FSPL_dB ...
         + rx_gain_dBi ...
         - rx_feeder_loss_dB ...
         - other_losses_dB;

Pr_dBm = Pr_dBW + 30;

fprintf('SAT-03 LINK BUDGET\n');
fprintf('FSPL          : %.2f dB\n', FSPL_dB);
fprintf('EIRP          : %.2f dBW\n', EIRP_dBW);
fprintf('Received power: %.2f dBW\n', Pr_dBW);
fprintf('Received power: %.2f dBm\n', Pr_dBm);