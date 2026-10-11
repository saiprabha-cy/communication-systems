%% SAT-04: EIRP Calculator
clear; clc;

tx_power_W = 1;
antenna_gain_dBi = 2;
feeder_loss_dB = 1;
pointing_loss_dB = 0;  % Set nonzero if applicable

tx_power_dBW = 10*log10(tx_power_W);

EIRP_dBW = tx_power_dBW ...
           + antenna_gain_dBi ...
           - feeder_loss_dB ...
           - pointing_loss_dB;

EIRP_dBm = EIRP_dBW + 30;
EIRP_W_equivalent = 10^(EIRP_dBW/10);

fprintf('SAT-04 EIRP\n');
fprintf('EIRP: %.2f dBW\n', EIRP_dBW);
fprintf('EIRP: %.2f dBm\n', EIRP_dBm);
fprintf('Equivalent isotropic power: %.3f W\n', ...
    EIRP_W_equivalent);