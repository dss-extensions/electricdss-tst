clc;
[DSSStartOK, DSSObj, DSSText] = DSSStartup;
DSSCircuit      =   DSSObj.ActiveCircuit;
DSSText.Command =   'ClearAll';             % Clears all instances of OpenDSS-PM
DSSText.Command =   'Set Parallel=Yes';             % Clears all instances of OpenDSS-PM

DSSParallel     =   DSSCircuit.Parallel;    % Habdler for Parallel processing functions
CPUs            =   DSSParallel.NumCPUs;    % Gets how many CPUs this PC has
% By default one actor is created by default, if you want more than one
% parallel instance you will have to create them. Try to leave at least
% One CPU available to handle the rest of windows, otherwise will block
% Everything
disp('Creating Actors');
for i=1:CPUs-1,
    if i ~= 1,
        DSSParallel.CreateActor; % Creates additonal actors
    end;
    DSSText.Command =   'compile (C:\Program Files\OpenDSS\EPRITestCircuits\ckt5\Master_ckt5.DSS)';
    DSSCircuit.Solution.Solve;    
    DSSParallel.Wait;   % for the first solve, it is needed to wait before creating other actor
    DSSText.Command =   'set mode=Time stepsize=1h number=16000';
end;
% Now the actors are solved
disp('Simulation Started');
DSSCircuit.Solution.SolveAll;
pause(0.1); 
hold on;
BoolStatus      =   0;
while BoolStatus == 0,
    ActorStatus     =   DSSParallel.ActorStatus;
    BoolStatus      =   all(ActorStatus & 1); %Checks if everybody has ended
    ActorProgress   =   DSSParallel.ActorProgress;
    bar(ActorProgress);
    axis([0 (CPUs) 0 100]);
    xlabel('Actor #');
    ylabel('Actor progress (%)');
    pause(0.5);  %  A little wait to not saturate the Processor  
end;
disp('Simulation finished by all the actors');

