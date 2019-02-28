% This example works with OpenDSS version 8.5.4.1 and later
clc;
[DSSStartOK, DSSObj, DSSText] = DSSStartup;
DSSCircuit      =   DSSObj.ActiveCircuit;
DSSText.Command =   'ClearAll';             % Clears all instances of OpenDSS-PM
DSSText.Command =   'Set Parallel=No';      % Parallel Suite off

DSSParallel     =   DSSCircuit.Parallel;    % Habdler for Parallel processing functions
CPUs            =   DSSParallel.NumCPUs-1;    % Gets how many CPUs this PC has
% By default one actor is created, if you want more than one
% parallel instance you will have to create them. Try to leave at least
% One CPU available to handle the rest of windows, otherwise will block
% Everything
disp('Creating Actors');
DSSText.Command =   'compile "C:\Program Files\OpenDSS\EPRITestCircuits\ckt5\Master_ckt5.DSS"';
DSSText.Command =   'set maxiterations=1000 maxcontroliter=1000';   % Just in case
DSSCircuit.Solution.Solve;                      % Solves Actor 1
DSSText.Command =   ['Clone ',int2str(CPUs-2)]; %Creates the other actors
DSSText.Command =   'set ActiveActor=*';        %activates all actors to send commands concurrently
DSSText.Command =   'set mode=Time stepsize=1h number=16000';
% to send commands to each actor separately you need to select each actor
% indepedently
DSSText.Command =   'set ActiveActor=1'; % Go back to actor 1
DSSText.Command =   'Set Parallel=Yes';   % Activates the parallel features
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

