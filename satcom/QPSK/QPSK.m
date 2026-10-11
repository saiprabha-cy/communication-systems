%% SAT-09: QPSK Satellite Link - Modulator
clear; clc; close all;

% Input bits; even number required
bits = [0 0  0 1  1 1  1 0  1 0  0 0];

if mod(length(bits), 2) ~= 0
    error('QPSK requires an even number of input bits.');
end

% Group bits into pairs
pairs = reshape(bits, 2, []).';

% Gray mapping used in this example
symbols = zeros(size(pairs, 1), 1);

for k = 1:size(pairs, 1)
    b1 = pairs(k,1);
    b2 = pairs(k,2);

    I = 1 - 2*b2;
    Q = 1 - 2*b1;

    symbols(k) = (I + 1i*Q)/sqrt(2);
end

disp('Input bit pairs:');
disp(pairs);

disp('QPSK symbols:');
disp(symbols);

figure;
plot(real(symbols), imag(symbols), 'o', 'MarkerSize', 9);
xlabel('In-phase (I)');
ylabel('Quadrature (Q)');
title('SAT-09: QPSK Constellation');
axis equal;
xlim([-1.5 1.5]);
ylim([-1.5 1.5]);
grid on;