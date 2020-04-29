% Max power output for the storage device = 2000MVA
Vref        =   mean(Vpu); % the V reference is the mean of the 3 phase, could change
% Checks the range in which Vref respect to the control curve
Xref        =   VVar_Curve(1,:);
maxp        =   size(Xref);
vvar_idx    =   1; % To store the index where Vref is found
idx_found   =   0; % A flag to say we are done
while idx_found == 0,
    if (Vref >= Xref(vvar_idx)) && (Vref <= Xref(vvar_idx+1)),
        idx_found   =   1;      % this is the range where Vref belongs
    else
        vvar_idx    =   vvar_idx + 1;
        if vvar_idx > maxp(2),
            idx_found   =   2; % Just in case the value has gone crazy
        end;
    end;
end;
kWIsON  =   0;              % The amount of kW delivered by the Storage
if idx_found == 1,          % checks that there was no error to keep going
    Estimate_Ctrl_point;    % Estimates the vars output in pu
    if (time >= Storage_time(1)) && (time <= Storage_time(2)),
        DSSText.Command =   'generator.StorageSm.kW = 500'; %Turns On the storage output
        kWIsON          =   500;
    else
        DSSText.Command =   'generator.StorageSm.kW = 0.01';%Turns OFF the storage output
    end;
    kwatts  =   [kwatts kWIsON];            % Records the current value (kW)
    Akvar   =   sqrt(2000^2 - kWIsON^2);    % The amount of available kvar
    Akvar   =   Akvar*VarsPU;               % The amount of vars that should be comming out
    DSSText.Command =   ['generator.StorageSm.kvar = ', num2str(Akvar)];
    kvars   =   [kvars Akvar];              % Records the current value (kvar)
end;
