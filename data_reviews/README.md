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

Only developed and tested with Matlab 2020a. Not sure how it will do with 
earlier versions.
 
To request data via the M2M system, you will need to have the python code
available in the [ooi-data-explorations](https://github.com/oceanobservatories/ooi-data-explorations/tree/master/python) repository installed on your system
per the directions in the [README](https://github.com/oceanobservatories/ooi-data-explorations/blob/master/python/README.md). Then you need to "register" it with Matlab
so it knows to use that python environment. I use a `startup.m` file in my
Matlab home directory with the following code:

``` matlab
% startup.m
username = getenv('username');
setenv('PYTHONUNBUFFERED', '1');
setenv('path', ['C:\Users\' username '\Anaconda3\envs\ooi;', ...
    'C:\Users\' username '\Anaconda3\envs\ooi\Library\mingw-w64\bin;', ...
    'C:\Users\' username '\Anaconda3\envs\ooi\Library\usr\bin;', ...
    'C:\Users\' username '\Anaconda3\envs\ooi\Library\bin;', ...
    'C:\Users\' username '\Anaconda3\envs\ooi\Scripts;', ...
    'C:\Users\' username '\Anaconda3\envs\ooi\bin;', ...
    getenv('path')])
[~] = pyenv('Version',['C:\Users\' username '\Anaconda3\envs\ooi\pythonw.exe'],...         
    'ExecutionMode','InProcess');
clear username
```

Finally you need to setup your access credentials, so Matlab can access the OOI
M2M API. In Matlab:

``` matlab
options = weboptions('Username', <API Username>, 'Password', <API Token>);
save('ooinet.credentials.mat', 'options');
```

Put the `ooinet.credentials.mat` file in your Matlab path (best option is the
Matlab home directory) and it will be available for use any time you want to 
access the OOI M2M API without having to put your credentials actually into the
code.