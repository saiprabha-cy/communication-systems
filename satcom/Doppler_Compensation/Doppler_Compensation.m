%% SAT-13: Doppler Compensation using a Known BPSK Preamble
clear; clc; close all;
rng(13);

% Simulation parameters
Fs = 100e3;              % One sample per symbol
Npre = 256;
Ndata = 4000;
cfoHz = 1500;            % Illustrative residual frequency offset
EbN0_dB = 12;

% Known preamble: all bits are 1, so BPSK symbols are +1
preambleBits = ones(Npre,1);
dataBits = randi([0 1],Ndata,1);
bits = [preambleBits; dataBits];

% BPSK mapping: 0 -> -1, 1 -> +1
tx = 2*bits - 1;
n = (0:length(tx)-1).';

% Apply carrier-frequency offset
rxCFO = tx .* exp(1j*2*pi*cfoHz*n/Fs);

% Add complex AWGN for the selected Eb/N0
gamma = 10^(EbN0_dB/10);
sigma = sqrt(1/(2*gamma));
noise = sigma*(randn(size(tx)) + 1j*randn(size(tx)));
rx = rxCFO + noise;

% Estimate offset using only the known preamble
pre = rx(1:Npre);
phaseProducts = pre(2:end).*conj(pre(1:end-1));
estimatedCFO = Fs/(2*pi)*angle(sum(phaseProducts));

% Compensate frequency offset
rxCorrected = rx .* exp(-1j*2*pi*estimatedCFO*n/Fs);

% Hard-decision BPSK detection on payload only
rxPayload = rxCorrected(Npre+1:end);
detectedBits = real(rxPayload) >= 0;

BER = mean(detectedBits ~= dataBits);

fprintf('SAT-13: DOPPLER COMPENSATION\n');
fprintf('Actual offset:    %.2f Hz\n',cfoHz);
fprintf('Estimated offset: %.2f Hz\n',estimatedCFO);
fprintf('Estimation error: %.2f Hz\n',estimatedCFO-cfoHz);
fprintf('Payload BER:      %.6g\n',BER);

% Plot received phase rotation before and after compensation
figure;
subplot(2,1,1);
plot(n(1:500)/Fs, unwrap(angle(rx(1:500))));
xlabel('Time (s)');
ylabel('Phase (rad)');
title('Received Phase Before Compensation');
grid on;

subplot(2,1,2);
plot(n(1:500)/Fs, unwrap(angle(rxCorrected(1:500))));
xlabel('Time (s)');
ylabel('Phase (rad)');
title('Received Phase After Compensation');
grid on;