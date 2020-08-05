# OOI Data Review Tool -- Initial Draft
Uses a Matlab App to request and load data downloaded from the OOI system for 
review, with the ability to either download associated annotations (after the 
site, node and stream are specified), or load locally saved annotations. Basic
workflow is to load locally saved data, plot selected variables, review, create,
or update annotations, save those annotations locally and repeat. Can be used
to formally review the data for a particular instrument (e.g. download and save 
all the PHSEN data for the CE01ISSM NSIF and create, update, or correct 
annotations associated with the different data types such as recovered_host or 
recovered_inst) or just to quickly peruse datasets to get a sense of overall
performance.

## Usage
`TODO`

## Assumptions
Developed and tested with Matlab 2019b and 2020a.  Earlier versions will not be
supported.

### Access Credentials for the OOI M2M API
In order to access the OOI M2M API, you need to setup your OOINet credentials as
a `weboptions` object that Matlab can then use as part of a `webread` request
to the API.  To set this up, in Matlab (replacing `<API Username>` and 
`<API Token>` with your OOINet credentials):

``` matlab
>> username = '<API Username>';
>> password = '<API Token>';
>> options = weboptions('Timeout', 180, 'HeaderFields', {'Authorization', ...
                 ['Basic ' matlab.net.base64encode([username ':' password])]});
>> save('ooinet.credentials.mat', 'options');
```

Put the `ooinet.credentials.mat` file in your Matlab path (best option is your
Matlab home directory as it is on the Matlab path by default) so it is available
for this application.  The GUI uses these credentials to put together the 
hierarchical data request structure and to pull annotations.

### Setup for M2M Data Requests
To request data via the M2M system (after structuring the request using the
hierarchical dropdowns to bound the request) you will need to have the python
code available in the [ooi-data-explorations](https://github.com/oceanobservatories/ooi-data-explorations/tree/master/python) 
repository installed on your system per the directions in the 
[README](https://github.com/oceanobservatories/ooi-data-explorations/blob/master/python/README.md). 
Then you need to "register" it with Matlab so it knows to use that python 
environment (Matlab does not support Anaconda, so it needs to be explicitly
setup to use the correct code). I use a `startup.m` file in my Matlab home 
directory with the following code:

``` matlab
% startup.m
username = getenv('username');
setenv('PYTHONUNBUFFERED', '1');
setenv('path', ['C:\Users\' username '\Anaconda3\envs\ooi;', ...
       'C:\Users\' username '\Anaconda3\envs\ooi\Library\bin;', ...
       'C:\Users\' username '\Anaconda3\envs\ooi\Library\lib;', ...
       getenv('path')])
[~] = pyenv('Version',['C:\Users\' username '\Anaconda3\envs\ooi\pythonw.exe'], ...
            'ExecutionMode','InProcess');
clear username
```
This works on a PC. Mac/Linux users will need to adjust the base paths 
according to whereever Anaconda was installed, remove `Library` from the path 
string, and change the `pyenv` settings. For example, the above `startup.m`
becomes the following on my Linux machine:

``` matlab
% startup.m
username = getenv('username');
setenv('PYTHONUNBUFFERED', '1');
setenv('path', ['/home/' username '/anaconda3/envs/ooi;', ...
       '/home/' username '/anaconda3/envs/ooi/bin;', ...
       '/home/' username '/anaconda3/envs/ooi/lib;', ...
       getenv('path')])
[~] = pyenv('Version',['/home/' username '/anaconda3/envs/ooi/python'], ...
            'ExecutionMode','InProcess');
clear username
```

To confirm that you have setup Matlab correctly, you can run the following set
of commands as a test:
``` matlab
>> py.math.exp(1)

ans =

    2.7183

>> np = py.importlib.import_module('numpy');
>> np.exp(1)

ans =

    2.7183

>> od = py.importlib.import_module('ooi_data_explorations.common');
>> od.list_nodes('CE01ISSM')

ans = 

  Python list with no properties.

    ['MFC31', 'MFD35', 'MFD37', 'RID16', 'SBC11', 'SBD17']
```