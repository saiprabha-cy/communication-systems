%% SAT-11: BER vs Eb/N0 for BPSK and QPSK over AWGN
clear; clc; close all;
rng(11);

EbN0_dB = 0:2:12;
Nbits = 200000;

berBPSK = zeros(size(EbN0_dB));
berQPSK = zeros(size(EbN0_dB));
berTheory = zeros(size(EbN0_dB));

for k = 1:length(EbN0_dB)

    gamma = 10^(EbN0_dB(k)/10);

    %% BPSK simulation
    bitsB = randi([0 1], Nbits, 1);
    txB = 2*bitsB - 1;  % Unit bit energy

    sigmaB = sqrt(1/(2*gamma));
    rxB = txB + sigmaB*randn(Nbits,1);

    bitsB_hat = rxB >= 0;
    berBPSK(k) = mean(bitsB_hat ~= bitsB);

    %% QPSK simulation: two bits per unit-energy symbol
    bitsQ = randi([0 1], Nbits, 1);
    pairs = reshape(bitsQ, 2, []).';

    % Same Gray mapping as SAT-09
    I = 1 - 2*pairs(:,2);
    Q = 1 - 2*pairs(:,1);
    txQ = (I + 1i*Q)/sqrt(2);

    % Es = 1, Eb = Es/2 = 1/2
    % Therefore N0 = Eb/gamma = 1/(2*gamma)
    % Each real noise component has variance N0/2.
    sigmaQ = sqrt(1/(4*gamma));

    noiseQ = sigmaQ * ...
        (randn(size(txQ)) + 1i*randn(size(txQ)));

    rxQ = txQ + noiseQ;

    % Hard-decision detection for the defined Gray mapping
    bitsQ_hat = zeros(size(pairs));
    bitsQ_hat(:,2) = real(rxQ) < 0;
    bitsQ_hat(:,1) = imag(rxQ) < 0;

    detectedQ = reshape(bitsQ_hat.', [], 1);
    berQPSK(k) = mean(detectedQ ~= bitsQ);

    %% Ideal coherent BPSK/QPSK BER
    berTheory(k) = 0.5*erfc(sqrt(gamma));
end

%% Display results
fprintf('Eb/N0(dB)   BPSK BER       QPSK BER       Theory BER\n');

for k = 1:length(EbN0_dB)
    fprintf('%8.1f   %12.6g   %12.6g   %12.6g\n', ...
        EbN0_dB(k), berBPSK(k), berQPSK(k), berTheory(k));
end

%% Plot
figure;
semilogy(EbN0_dB, berBPSK, 'o-', 'LineWidth', 1.5);
hold on;
semilogy(EbN0_dB, berQPSK, 's-', 'LineWidth', 1.5);
semilogy(EbN0_dB, berTheory, '--', 'LineWidth', 1.5);

xlabel('E_b/N_0 (dB)');
ylabel('Bit Error Rate (BER)');
title('SAT-11: BER vs E_b/N_0 over AWGN');
legend('BPSK simulated', 'QPSK simulated', ...
    'Ideal BPSK/QPSK theory', 'Location', 'southwest');
grid on;
ylim([1e-6 1]);