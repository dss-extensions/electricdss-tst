    clear all;
    clc;
    DSSObj = actxserver('OpenDSSEngine.DSS');
    if ~DSSObj.Start(0),
    disp('Unable to start the OpenDSS Engine');
    return
    end
   %Generates random loadprofiles for each load (3 loads total)
    LS_LD   =   zeros(24,3);
    for i=1:24,
        for j=1:3,
            LS_LD(i,j)   =   rand;
        end;
    end
  
    DSSText     = DSSObj.Text; 
    DSSCircuit  = DSSObj.ActiveCircuit;
    DSSSolution = DSSCircuit.Solution;
    DSSLoad     = DSSCircuit.Loads;
    Projpath    = [pwd,'\IEEE_519.dss'];
    DSSText.Command='Clear';
    DSSText.Command=['Compile "',Projpath,'"'];    
%Gets the names and nominal powers (P) for each load    
%You can improev this routine to include all the circuit's loads
    LD_P    =   zeros(3,1);
    DSSLoad.First;
    for i=1:3,
        LD_P(i)    =   DSSLoad.kw;
        DSSLoad.Next;
    end;

    DSSText.Command='set mode=harmonicT stepsize=1h';
% Starts the simulation
      for i=1:24,
     %sets the load value for each load
         DSSLoad.First;
         for j=1:3,
             DSSLoad.kw  =   LS_LD(i,j)*LD_P(j);   
             DSSLoad.Next;
         end;
         DSSSolution.Solve;
      end;
      DSSText.Command    =   'show monitor MPCC';

