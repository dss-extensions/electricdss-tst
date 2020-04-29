Vputemp     =   DSSBus.PuVoltages;  % Vpu in complex format
numiter     =   size(Vputemp);
Vpu         =   zeros(numiter(2)/2,1);
local_idx   =   1;
for idx_tmp=1:2:numiter(2),
    Vpu(local_idx)      =   sqrt(Vputemp(idx_tmp)^2 + Vputemp(idx_tmp+1)^2);
    local_idx           =   local_idx+1;
end;