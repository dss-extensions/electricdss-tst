clc;
[DSSStartOK, DSSObj, DSSText] = DSSStartup;
DSSCircuit      =   DSSObj.ActiveCircuit;
DSSText.Command =   'ClearAll';             % Clears all instances of OpenDSS-PM
DSSText.Command =   'Set Parallel=No';      % Deactivates parallel processing

DSSParallel     =   DSSCircuit.Parallel;    % Habdler for Parallel processing functions
CPUs            =   DSSParallel.NumCPUs;    % Gets how many CPUs this PC has
% By default one actor is created by default, if you want more than one
% parallel instance you will have to create them. Try to leave at least
% One CPU available to handle the rest of windows, otherwise will block
% Everything
% Prepares everything for a yearly simulation using temporal parallelization
YDelta  =   8760/(CPUs-1);
disp('Compiling and creating Actors');
for i=1:CPUs-1,
    if i ~= 1,
        DSSParallel.CreateActor; % Creates additonal actors
    end;
    DSSText.Command =   'compile (C:\Program Files\OpenDSS\EPRITestCircuits\ckt7\Master_ckt7.DSS)';
    DSSCircuit.Solution.Solve;    
    if i == (CPUs-1),
        YDelta = 8760 - (CPUs-2)*YDelta;
    end;
    DSSText.Command =   ['set mode=Yearly number=',int2str(YDelta),' hour=',int2str((i-1)*YDelta)];
end;
% Now the actors are solved
DSSText.Command =   'Set Parallel=Yes';             % Activates parallel processing
DSSCircuit.Solution.SolveAll;

pause(0.1); 
BoolStatus      =   0;
while BoolStatus == 0,
    ActorStatus     =   DSSParallel.ActorStatus;
    BoolStatus      =   all(ActorStatus & 1); %Checks if everybody has ended
    clc;
    % Prints the current time on each simulation
    for i = 1:(CPUs-1),
        DSSParallel.ActiveActor = i;
        CHour   =   DSSCircuit.Solution.dblhour;
        fprintf('Actor %i Time(hours) : %f\n',i,CHour);
    end;
    pause(0.5);  %  A little wait to not saturate the Processor  
end;
disp('Simulation finished by all the actors');

