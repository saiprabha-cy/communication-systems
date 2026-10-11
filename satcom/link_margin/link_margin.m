%% SAT-07: Satellite Link Margin
clear; clc;

% Illustrative link values from SAT-03 and SAT-06
actual_CN_dB = 22.37;

% Example threshold only; choose this from the actual receiver design
required_CN_dB = 10.0;

% Additional design allowance for uncertainty
reserve_dB = 3.0;

raw_margin_dB = actual_CN_dB - required_CN_dB;
margin_after_reserve_dB = raw_margin_dB - reserve_dB;

fprintf('SAT-07 LINK MARGIN\n');
fprintf('Actual C/N              : %.2f dB\n', actual_CN_dB);
fprintf('Required C/N            : %.2f dB\n', required_CN_dB);
fprintf('Raw link margin         : %.2f dB\n', raw_margin_dB);
fprintf('Reserve allowance       : %.2f dB\n', reserve_dB);
fprintf('Margin after reserve    : %.2f dB\n', ...
    margin_after_reserve_dB);

if margin_after_reserve_dB >= 0
    fprintf('Result: Meets illustrative requirement.\n');
else
    fprintf('Result: Does not meet illustrative requirement.\n');
end