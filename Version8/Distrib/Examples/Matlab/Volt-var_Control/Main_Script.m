clc;
% Initialize OpenDSS
[DSSStartOK, DSSObj, DSSText] = DSSStartup;
DSSCircuit      =   DSSObj.ActiveCircuit;
DSSBus          =   DSSCircuit.ActiveBus;
DSSElement      =   DSSCircuit.ActiveCktElement;

get(DSSCircuit)

% Local registers to show curves at the end
kvars           =   [];
kwatts          =   [];
demand          =   [];

% The Volt-var control curve
VVar_Curve      =   [0.4 0.89 0.99 0.99 0.99 1.09 1.6;...
                     1   1    0    0    0   -1   -1];
Storage_time    =   [14 18];          % The time interval in which the storage will deliver watts
Storage_W       =   500;            % Output in kWh
figure('name','Volt-var control curve');                 
plot(VVar_Curve(1,:),VVar_Curve(2,:));
axis([0.4 1.6 -1.1 1.1]);
grid on;
DSSText.Command =   'Clear'; 
DSSText.Command =   'compile (C:/Program Files/OpenDSS/IEEETestCases/123Bus/IEEE123Master.dss)';

% Creates the generator to emulate the storage device
DSSText.Command =   'New generator.StorageSm bus1=79 kv=4.16 phases=3 kw=0.1 kvar=0.1';
DSSText.Command =   'New Monitor.FeederHead element=Line.L115 term=1';  % To register V at feeder head
% Creating the load profile (In the case you want to apply a load profile
%DSSText.Command =   'New Loadshape.Mydemand npts=1440, minterval=1, csvfile=Ld_profile.csv'; 
%DSSText.Command =   'batchedit Load..* daily=Mydemand'; % Apply to all loads
DSSText.Command =   'set mode=snap';
DSSCircuit.Solution.Solve;    
DSSText.Command =   'set mode=daily stepsize=1h number=1';
Xtime           =   [];
% Simulation starts
for time=1:24,                      % daily simulation
    DSSCircuit.Solution.Solve;
    DSSCircuit.SetActiveBus('79');  % this is the bus where the generator is connected
    Get_Vpu_AtBus;                  % Gets the Vpu at the bus
    VVar_Controller;                % Execute external Control Actions
    Xtime       =   [Xtime time];   % Records the simulation time
    DSSCircuit.SetActiveElement('Line.L115');
    Powers      =   DSSElement.powers;
    demand      =   [demand Powers(1) + Powers(3) + Powers(5)];
end;

%plot results
figure('name','vars delivered by the storage'); 
plot(Xtime,kvars);
figure('name','Watts delivered by the storage');
plot(Xtime,kwatts);
figure('name','Demand (kW)');
plot(Xtime,demand);

%DSSText.Command =   'show Monitor FeederHead';

% Simulation ends
disp('Simulation finished');
