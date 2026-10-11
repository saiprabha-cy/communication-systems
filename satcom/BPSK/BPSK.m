%% SAT-08: BPSK Satellite Link - Modulator
clear; clc; close all;

bits = [1 0 1 1 0 0 1 0];

% BPSK mapping: 0 -> -1, 1 -> +1
symbols = 2*bits - 1;

fprintf('Input bits:\n');
disp(bits);

fprintf('BPSK symbols:\n');
disp(symbols);

figure;
stem(0:length(bits)-1, symbols, 'filled');
xlabel('Symbol index');
ylabel('BPSK amplitude');
title('SAT-08: BPSK Symbol Mapping');
ylim([-1.5 1.5]);
grid on;

% Optional Communications Toolbox cross-check
if exist('pskmod', 'file') == 2
    toolboxSymbols = pskmod(bits(:), 2, 0, 'gray');
    fprintf('PSK modulator is available for cross-checking.\n');
    disp('Toolbox output:');
    disp(toolboxSymbols.');
end