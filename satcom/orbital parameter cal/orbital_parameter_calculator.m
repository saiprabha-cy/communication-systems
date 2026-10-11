%% SAT-01: Orbital Parameter Calculator
% Model: Ideal two-body orbit around Earth
% Units: km, seconds, radians

clear;
clc;

%% Earth constants
mu = 398600.4418;       % Earth gravitational parameter (km^3/s^2)
Re = 6378.137;          % Reference equatorial radius (km)

%% User inputs
altitude_km = 550;      % Initial circular-orbit altitude (km)
eccentricity = 0.0;     % 0 = circular orbit

%% Input validation
if altitude_km <= 0
    error('Altitude must be greater than zero.');
end

if eccentricity < 0 || eccentricity >= 1
    error('For this elliptical-orbit calculator, use 0 <= e < 1.');
end

%% Orbital geometry
rp = Re + altitude_km;  % Initial radius at perigee (km)

% Calculate semi-major axis from perigee radius and eccentricity
a = rp / (1 - eccentricity);

ra = a * (1 + eccentricity);  % Apogee radius (km)

perigee_altitude = a * (1 - eccentricity) - Re;
apogee_altitude = ra - Re;

%% Orbital period
T = 2 * pi * sqrt(a^3 / mu);

%% Orbital velocity
% Vis-viva equation at perigee
v_perigee = sqrt(mu * (2/rp - 1/a));

% Vis-viva equation at apogee
v_apogee = sqrt(mu * (2/ra - 1/a));

%% Mean motion
mean_motion_rad_s = sqrt(mu / a^3);
mean_motion_rev_day = mean_motion_rad_s * 86400 / (2*pi);

%% Specific orbital energy
specific_energy = -mu / (2*a);

%% Display results
fprintf('\n====================================\n');
fprintf(' SAT-01 ORBITAL PARAMETER CALCULATOR\n');
fprintf('====================================\n');

fprintf('Semi-major axis       : %.3f km\n', a);
fprintf('Eccentricity          : %.4f\n', eccentricity);

fprintf('Perigee altitude      : %.3f km\n', ...
    perigee_altitude);

fprintf('Apogee altitude       : %.3f km\n', ...
    apogee_altitude);

fprintf('Orbital period        : %.2f seconds\n', T);
fprintf('Orbital period        : %.2f minutes\n', T/60);

fprintf('Perigee velocity      : %.4f km/s\n', ...
    v_perigee);

fprintf('Apogee velocity       : %.4f km/s\n', ...
    v_apogee);

fprintf('Mean motion           : %.6f rad/s\n', ...
    mean_motion_rad_s);

fprintf('Mean motion           : %.4f rev/day\n', ...
    mean_motion_rev_day);

fprintf('Specific energy       : %.4f km^2/s^2\n', ...
    specific_energy);

fprintf('====================================\n');