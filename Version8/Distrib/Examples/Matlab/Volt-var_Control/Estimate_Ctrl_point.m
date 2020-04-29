% Routine to estimate the control point in Vars
M       =   [0 1; 0 1]; 
P       =   [0; 0];
M(1,1)  =   VVar_Curve(1,vvar_idx);
M(2,1)  =   VVar_Curve(1,vvar_idx+1);
P(1)    =   VVar_Curve(2,vvar_idx);
P(2)    =   VVar_Curve(2,vvar_idx+1);
Eq      =   inv(M)*P;
VarsPU  =   Eq(1)*Vref+Eq(2);
