%% SAT-14: End-to-End Satellite Telemetry Link
clear; clc; close all;
rng(14);

%% Link parameters
Fs = 100e3;               % Sample rate (one sample/symbol)
cfoHz = 1200;             % Residual frequency offset
EbN0_dB = 12;             % Normalized bit-energy-to-noise-density ratio
preambleBits = 256;       % Known acquisition sequence

%% Build an educational telemetry payload
% Sequence number: 1 byte
% Temperature: signed int16, tenths of a degree C
% Battery: uint16, millivolts
sequence = uint8(7);
temperature_C = 24.6;
battery_V = 3.82;

tempRaw = int16(round(temperature_C*10));
batteryRaw = uint16(round(battery_V*1000));

% Payload byte order: little-endian
payload = uint8([
    sequence, ...
    typecast(tempRaw,'uint8'), ...
    typecast(batteryRaw,'uint8')
]);

%% Append CRC-16/X.25
crc = crc16_x25(payload);

% CRC bytes sent least-significant byte first
crcBytes = uint8([bitand(crc,255), bitshift(crc,-8)]);

frame = [payload, crcBytes];

%% Convert bytes to serial bits, MSB first
frameBits = reshape( ...
    bitget(frame, 8:-1:1).', [], 1);

% Use an all-ones known preamble
txBits = [ones(preambleBits,1); frameBits];

%% BPSK modulation
txSymbols = 2*double(txBits) - 1;

n = (0:length(txSymbols)-1).';

%% Introduce frequency offset
rxCFO = txSymbols .* exp(1j*2*pi*cfoHz*n/Fs);

%% Add complex AWGN
gamma = 10^(EbN0_dB/10);
sigma = sqrt(1/(2*gamma));

noise = sigma*(randn(size(txSymbols)) ...
    + 1j*randn(size(txSymbols)));

rx = rxCFO + noise;

%% Estimate frequency offset using known preamble
pre = rx(1:preambleBits);
products = pre(2:end).*conj(pre(1:end-1));

estimatedCFO = Fs/(2*pi)*angle(sum(products));

%% Compensate
rxCorrected = rx .* ...
    exp(-1j*2*pi*estimatedCFO*n/Fs);

%% Detect payload bits
payloadRx = rxCorrected(preambleBits+1:end);
detectedBits = real(payloadRx) >= 0;

BER = mean(detectedBits ~= frameBits);

%% Reconstruct bytes (MSB first)
bitMatrix = reshape(detectedBits, 8, []).';

rxBytes = uint8(zeros(1,size(bitMatrix,1)));

for k = 1:size(bitMatrix,1)
    value = uint8(0);

    for b = 1:8
        value = bitshift(value,1) ...
            + uint8(bitMatrix(k,b));
    end

    rxBytes(k) = value;
end

%% Verify CRC
receivedPayload = rxBytes(1:end-2);
receivedCRC = double(rxBytes(end-1)) ...
    + 256*double(rxBytes(end));

calculatedCRC = crc16_x25(receivedPayload);
crcValid = receivedCRC == calculatedCRC;

%% Decode telemetry only if CRC passes
fprintf('\nSAT-14: TELEMETRY LINK RESULTS\n');
fprintf('Actual CFO:       %.2f Hz\n',cfoHz);
fprintf('Estimated CFO:    %.2f Hz\n',estimatedCFO);
fprintf('Estimation error: %.2f Hz\n',estimatedCFO-cfoHz);
fprintf('Eb/N0:            %.2f dB\n',EbN0_dB);
fprintf('Bit error rate:   %.6g\n',BER);
fprintf('CRC valid:        %d\n',crcValid);

if crcValid
    rxSequence = receivedPayload(1);

    rxTempRaw = typecast( ...
        uint8(receivedPayload(2:3)), 'int16');

    rxBatteryRaw = typecast( ...
        uint8(receivedPayload(4:5)), 'uint16');

    rxTemperature_C = double(rxTempRaw)/10;
    rxBattery_V = double(rxBatteryRaw)/1000;

    fprintf('Sequence:         %u\n',rxSequence);
    fprintf('Temperature:      %.1f C\n',rxTemperature_C);
    fprintf('Battery voltage:  %.3f V\n',rxBattery_V);
else
    fprintf('Frame rejected: CRC verification failed.\n');
end

function crc = crc16_x25(data)
    % CRC-16/X.25 (reflected polynomial 0x8408)
    crc = uint16(65535);

    for k = 1:numel(data)
        crc = bitxor(crc, uint16(data(k)));

        for b = 1:8
            if bitand(crc,uint16(1))
                crc = bitxor(bitshift(crc,-1),uint16(hex2dec('8408')));
            else
                crc = bitshift(crc,-1);
            end
        end
    end

    crc = bitcmp(crc);
end

%% Plot received constellation
figure;
scatter(real(rxCorrected(preambleBits+1:end)), ...
    imag(rxCorrected(preambleBits+1:end)), 16, 'filled');

xlabel('In-phase');
ylabel('Quadrature');
title('SAT-14: Received Telemetry Symbols After Compensation');
grid on;
