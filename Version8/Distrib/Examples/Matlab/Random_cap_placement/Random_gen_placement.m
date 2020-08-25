% This example works with OpenDSS version 8.5.9.1 and later
% here we are allocating an existing Cap in all the compatible buses
% around the circuit to see the impact at the PCC (bus 670).
% we are also randomly assigning the cap size.
% Latest update (01/13/2020).

clear;
clc;
[DSSStartOK, DSSObj, DSSText] = DSSStartup;
DSSCircuit      =   DSSObj.ActiveCircuit;
DSSBuses        =   DSSCircuit.ActiveBus;
disp('Compiling circuit');
DSSText.Command =   'compile "C:\Program Files\OpenDSS\IEEETestCases\13Bus\IEEE13Nodeckt.dss"';
DSSText.Command =   'set maxiterations=1000 maxcontroliter=1000';   % Just in case
DSSCircuit.Solution.Solve;
% Random Bus Allocation
Buses           =   DSSCircuit.AllBusNames;
Cap_list        =   DSSCircuit.Capacitor.AllNames;
%select cap 1 as the element to move across the circuit
Sel_cap         =   1;
DSSText.Command =   ['? Capacitor.',Cap_list{Sel_cap},'.kV'];
Cap_kV          =   str2num(DSSText.Result);
DSSText.Command =   ['? Capacitor.',Cap_list{Sel_cap},'.phases'];
Cap_numphases   =   str2num(DSSText.Result);
% The cap voltage is used in LN value
if (Cap_numphases == 3)
    Cap_kV   =   Cap_kV/sqrt(3);
end;
% Now we set the max kvar as the reference using the original kvar
DSSText.Command =   ['? Capacitor.',Cap_list{Sel_cap},'.kvar'];
max_kvar        =   str2num(DSSText.Result);

%Now evaluates the buses for which the voltage level the cap is compatible
%with
Bus_candidates   =   {};
for i=1:max(size(Buses)),
    DSSCircuit.SetActiveBus(Buses{i});
    if (DSSBuses.kVBase == Cap_kV)
        Bus_candidates{end + 1,1}  =   Buses{i};
    end;
end;
%Now we generate different a vector with different values for the cap
cap_kvar = zeros(max(size(Bus_candidates)),1);
for i = 1:max(size(Bus_candidates)),
    cap_kvar(i) = floor(rand()*max_kvar);
end;

%Start the simulation and store the voltages at the PCC (bus 670)
PCC_Volts       =   zeros(max(size(Bus_candidates)),6);
for i = 1:max(size(Bus_candidates)),
    DSSText.Command =   ['Capacitor.',Cap_list{Sel_cap},'.bus1=',Bus_candidates{i}];
    DSSText.Command =   ['Capacitor.',Cap_list{Sel_cap},'.kvar=',num2str(cap_kvar(i))];
    DSSCircuit.Solution.Solve;
    DSSCircuit.SetActiveBus('670');
    % reads the voltage a PCC
    PCC_Volts(i,:)  =   DSSBuses.VmagAngle;
end;

% Plot results
figure(1)
plot(PCC_Volts(:,1));
hold on;
plot(PCC_Volts(:,3));
plot(PCC_Volts(:,5));
title('Voltage at bus 670 (PCC) ');
xlabel('Candidate (bus) #');
ylabel('voltage at PCC');
legend({'Phase A','Phase B','Phase C'},'Location','southwest')

 
