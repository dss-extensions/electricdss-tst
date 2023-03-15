# Added by Paulo Meira for cross-compatibility with DSS Extensions

import os
if os.environ.get('USE_COM', '0') == '1':
    import win32com.client # pip install pywin32
    def get_dss_engine():
        return win32com.client.Dispatch("OpenDSSEngine.DSS")
        
    dss_suffix = 'COM'
else:
    from dss import DSS as dss_engine, set_case_insensitive_attributes
    
    # This is not recommended, but since it's third-party code, let's minimize the changes
    set_case_insensitive_attributes(True)
    
    def get_dss_engine():
        return dss_engine
       
    
    dss_suffix = 'DSSX'
