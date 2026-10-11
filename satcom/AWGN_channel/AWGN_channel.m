%% SAT-10: AWGN Channel
clear; clc; close all;
rng(10);  % Repeatable results

N = 2000;
EbN0_dB = 4;

% Random input bits and BPSK modulation
bits = randi([0 1], N, 1);
tx = 2*bits - 1;  % 0 -> -1, 1 -> +1

% Convert Eb/N0 from dB to linear
EbN0 = 10^(EbN0_dB/10);

% Unit-energy BPSK: Eb = 1
noiseSigma = sqrt(1/(2*EbN0));

% Add real Gaussian noise
noise = noiseSigma * randn(N,1);
rx = tx + noise;

% Coherent BPSK detection
detectedBits = rx >= 0;

errors = sum(detectedBits ~= bits);
measuredBER = errors/N;

fprintf('SAT-10: AWGN CHANNEL\n');
fprintf('Eb/N0: %.2f dB\n', EbN0_dB);
fprintf('Noise standard deviation: %.5f\n', noiseSigma);
fprintf('Bit errors: %d of %d\n', errors, N);
fprintf('Measured BER: %.6f\n', measuredBER);

figure;
subplot(1,2,1);
stem(tx(1:40), 'filled');
title('Transmitted BPSK symbols');
xlabel('Symbol index');
ylabel('Amplitude');
grid on;

subplot(1,2,2);
scatter(real(rx(1:500)), zeros(500,1), 12, 'filled');
title('Received symbols after AWGN');
xlabel('Received in-phase value');
ylabel('Quadrature value');
grid on;