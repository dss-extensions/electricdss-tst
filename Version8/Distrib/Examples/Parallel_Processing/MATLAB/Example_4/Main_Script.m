% This example works with OpenDSS version 8.5.4.1 and later
% In this example the aim is to control the regulators for parallel actors
% manually while controlling the simulation step by step every 15 min
% users can add monitors to verify the effects in voltage
clc;
[DSSStartOK, DSSObj, DSSText] = DSSStartup;
DSSCircuit      =   DSSObj.ActiveCircuit;
DSSObj.Allowforms=   false;
DSSText.Command =   'ClearAll';             % Clears all instances of OpenDSS-PM
DSSText.Command =   'Set Parallel=No';      % Parallel Suite off

DSSParallel     =   DSSCircuit.Parallel;    % Habdler for Parallel processing functions
CPUs            =   DSSParallel.NumCPUs-1;    % Gets how many CPUs this PC has
% By default one actor is created, if you want more than one
% parallel instance you will have to create them. Try to leave at least
% One CPU available to handle the rest of windows, otherwise will block
% Everything
disp('Creating Actors');
DSSText.Command =   'compile "C:\Program Files\OpenDSS\IEEETestCases\13Bus\IEEE13Nodeckt.dss"';
DSSText.Command =   'set maxiterations=1000 maxcontroliter=1000';   % Just in case
DSSCircuit.Solution.Solve;                      % Solves Actor 1
DSSText.Command =   ['Clone ',int2str(CPUs-2)]; %Creates the other actors
DSSText.Command =   'set ActiveActor=*';        %activates all actors to send commands concurrently
DSSText.Command =   'set mode=Time stepsize=15m number=1 controlmode=off'; %Deactivates controls
DSSText.Command =   'new monitor.FeederEnd element=line.671680 terminal=1 mode=0'; %Creates a monitor at the feeder end
% to send commands to each actor separately you need to select each actor
% indepedently
DSSText.Command =   'set ActiveActor=1';    % Go back to actor 1
DSSText.Command =   'Set Parallel=Yes';     % Activates the parallel features
XfmrList        =   {'reg1','reg2','reg3'}; % The list of regulators to play with
ListSize        =   size(XfmrList);
TapSize         =   2/320;                  % Number of taps per transformer
tapssel         =   [];
% Now the actors are solved
disp('Simulation Started');
for SimPrg = 1:96,
    DSSCircuit.Solution.SolveAll;
    DSSParallel.Wait;
    % At this point the simulation step is done, 
    for ActorIdx = 1:(CPUs-1),
        DSSParallel.ActiveActor     =   ActorIdx;
        %DSSText.Command             =   'Sample';
        % calculate the next tap to be set (randomly)
        NxtTap  =   round(rand*32)*TapSize + 0.9;
        for XfmrIdx = 1:ListSize(2),
            CMD                 =   ['Transformer.',XfmrList{XfmrIdx},'.tap=',num2str(NxtTap)];
            tapssel             =   [tapssel,CMD];
            DSSText.Command     =    CMD;
        end;
    end;
    clc;
    disp(['Current simulation time = ',int2str(SimPrg*15),' minutes']);
end;
disp('Simulation finished by all the actors');
% now read the monitors to show the differences
for ActorIdx = 1:(CPUs-1),
    DSSParallel.ActiveActor     =   ActorIdx;
    DSSCircuit.monitors.Name    =   'FeederEnd';                            %Selects the monitor 
    Freqs                       =   DSSCircuit.monitors.ByteStream;         %Request the Bytestream
    iMonitorDataSize            =   typecast(Freqs(9:12),'int32');          % To adjust the matrix
    VIMonitor                   =   typecast(Freqs(273:end),'single');      %Adjusts the content
    VIMonitor1                  =   reshape(VIMonitor(1:1022), iMonitorDataSize+2, [])';
    figure;
    plot(VIMonitor1(:,3));                                                  % phase 1
    hold on;
    plot(VIMonitor1(:,5));                                                  % phase 2
    hold on;
    plot(VIMonitor1(:,7));                                                  % phase 3
    title(['Results for Actor ',int2str(ActorIdx)]);
    xlabel('Time * 15 min');
    ylabel('voltage at feeder end');
    legend({'Phase A','Phase B','Phase C'},'Location','southwest')
    hold off;
end;



