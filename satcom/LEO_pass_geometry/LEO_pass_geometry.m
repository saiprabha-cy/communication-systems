%% SAT-02: LEO Pass Geometry Simulation
% Simplified circular orbit and spherical Earth model
% Coordinates: ECI satellite position, rotating-Earth ground station
% Units: km, seconds, degrees

clear;
clc;
close all;

%% Constants
mu = 398600.4418;       % Earth gravitational parameter (km^3/s^2)
Re = 6378.137;          % Reference Earth radius (km)
omegaEarth = 7.2921159e-5; % Earth rotation rate (rad/s)

%% Satellite orbit
altitude = 550;         % Satellite altitude (km)
a = Re + altitude;      % Circular orbit radius (km)
inclination = deg2rad(51.6);
raan = deg2rad(0);      % Right ascension of ascending node
u0 = deg2rad(0);        % Initial argument of latitude

n = sqrt(mu/a^3);       % Mean motion (rad/s)
period = 2*pi/n;        % Orbital period (s)

%% Ground station
latGS = deg2rad(13.0827);
lonGS = deg2rad(80.2707);
altGS = 0;              % Ground station altitude (km)

% Ground station ECEF position
rGS = (Re + altGS) * [
    cos(latGS)*cos(lonGS);
    cos(latGS)*sin(lonGS);
    sin(latGS)
];

%% Simulation time
dt = 10;                % Sample interval (s)
simulationDuration = 2*period;
t = (0:dt:simulationDuration).';

elevation = zeros(size(t));
range = zeros(size(t));

%% Propagate orbit and calculate elevation
for k = 1:length(t)

    % Circular orbit in the orbital plane
    u = u0 + n*t(k);

    rOrbital = a * [
        cos(u);
        sin(u);
        0
    ];

    % Rotate orbital-plane coordinates into ECI
    R3 = [
        cos(raan), -sin(raan), 0;
        sin(raan),  cos(raan), 0;
        0,          0,         1
    ];

    R1 = [
        1, 0, 0;
        0, cos(inclination), -sin(inclination);
        0, sin(inclination),  cos(inclination)
    ];

    rECI = R3 * R1 * rOrbital;

    % Rotate ground station from ECEF into ECI.
    % Longitude advances in the inertial frame with Earth rotation.
    theta = omegaEarth*t(k);

    Rearth = [
        cos(theta), -sin(theta), 0;
        sin(theta),  cos(theta), 0;
        0,            0,          1
    ];

    rGS_ECI = Rearth * rGS;

    % Satellite-to-ground relative position
    rho = rECI - rGS_ECI;

    range(k) = norm(rho);

    % Local East-North-Up basis at ground station
    east = [
        -sin(lonGS);
         cos(lonGS);
         0
    ];

    north = [
        -sin(latGS)*cos(lonGS);
        -sin(latGS)*sin(lonGS);
         cos(latGS)
    ];

    up = [
        cos(latGS)*cos(lonGS);
        cos(latGS)*sin(lonGS);
        sin(latGS)
    ];

    % Transform relative position into local ENU coordinates
    eastComponent = dot(rho, east);
    northComponent = dot(rho, north);
    upComponent = dot(rho, up);

    horizontalRange = hypot(eastComponent, northComponent);

    elevation(k) = atan2d(upComponent, horizontalRange);
end

%% Visibility analysis
minimumElevation = 10;  % Degrees
visible = elevation >= minimumElevation;

%% Print summary
fprintf('\nSAT-02: LEO PASS GEOMETRY\n');
fprintf('Satellite altitude : %.1f km\n', altitude);
fprintf('Orbital period     : %.2f minutes\n', period/60);
fprintf('Ground station     : Chennai example\n');
fprintf('Minimum elevation  : %.1f degrees\n', minimumElevation);
fprintf('Visible samples    : %d of %d\n', sum(visible), length(t));

% Identify contiguous visibility intervals
edges = diff([false; visible; false]);
passStarts = find(edges == 1);
passEnds = find(edges == -1) - 1;

fprintf('\nDetected visibility intervals:\n');

if isempty(passStarts)
    fprintf('No passes detected in this simulation window.\n');
else
    for p = 1:length(passStarts)
        startTime = t(passStarts(p));
        endTime = t(passEnds(p));

        fprintf('Pass %d: %.1f to %.1f seconds, duration %.1f seconds\n', ...
            p, startTime, endTime, endTime-startTime);
    end
end

%% Plot elevation versus time
figure;

plot(t/60, elevation, 'LineWidth', 1.5);
hold on;

yline(minimumElevation, '--', 'Minimum elevation');

xlabel('Time since simulation start (minutes)');
ylabel('Satellite elevation (degrees)');
title('SAT-02: LEO Satellite Pass Geometry');
grid on;

%% Plot satellite visibility
figure;

stairs(t/60, visible, 'LineWidth', 1.5);

xlabel('Time since simulation start (minutes)');
ylabel('Visible (1 = Yes, 0 = No)');
title('SAT-02: Ground Station Visibility');
ylim([-0.1 1.1]);
grid on;