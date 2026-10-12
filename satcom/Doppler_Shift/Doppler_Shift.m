%% SAT-12: Satellite Doppler Shift Simulation
clear; clc; close all;

% Constants
c = 299792458;          % Speed of light (m/s)
fc = 437e6;             % Carrier frequency (Hz)

% Illustrative radial-velocity profile:
% Negative = approaching; positive = receding
t = linspace(-300, 300, 601);  % Time (seconds)
vr = 7000 * sin(2*pi*t/1200);  % Radial velocity (m/s)

% First-order Doppler approximation
fd = -(vr/c) * fc;
frx = fc + fd;

fprintf('SAT-12: DOPPLER SHIFT\n');
fprintf('Carrier frequency: %.3f MHz\n', fc/1e6);
fprintf('Maximum absolute shift: %.2f Hz\n', max(abs(fd)));
fprintf('Minimum received frequency: %.6f MHz\n', min(frx)/1e6);
fprintf('Maximum received frequency: %.6f MHz\n', max(frx)/1e6);

figure;

subplot(2,1,1);
plot(t, vr/1000, 'LineWidth', 1.4);
xlabel('Time (s)');
ylabel('Radial velocity (km/s)');
title('Illustrative Satellite Radial Velocity');
grid on;

subplot(2,1,2);
plot(t, fd/1000, 'LineWidth', 1.4);
xlabel('Time (s)');
ylabel('Doppler shift (kHz)');
title('SAT-12: Doppler Shift at 437 MHz');
grid on;